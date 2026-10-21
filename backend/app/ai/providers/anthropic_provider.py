"""Proveedor de IA sobre la API de Anthropic (Claude) — US-007.

Este es el ÚNICO módulo del proyecto autorizado a importar el SDK `anthropic`
(regla no negociable #1 de CLAUDE.md, ADR-002). El resto del sistema solo ve
la interface agnóstica de `base_provider`. Las transformaciones puras (mensajes,
JSON, costos, backoff) viven en `anthropic_helpers.py`, que no importa el SDK.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator, Awaitable, Callable, Mapping
from typing import TYPE_CHECKING, Any

import anthropic
from pydantic import SecretStr

from app.ai.exceptions import (
    AIProviderError,
    ContentFilterError,
    ProviderUnavailableError,
    RateLimitError,
    UnsupportedTierError,
)
from app.ai.providers import anthropic_helpers as helpers
from app.ai.providers.base_provider import (
    CompletionRequest,
    CompletionResponse,
    LLMProvider,
    ModelTier,
    ToolCall,
    ToolResult,
    VisionProvider,
)
from app.core.config import ModelPricing
from app.core.logging import get_logger

if TYPE_CHECKING:
    from app.core.config import Settings

logger = get_logger(__name__)

PROVIDER_NAME = "anthropic"

SleepFn = Callable[[float], Awaitable[None]]


class AnthropicProvider(LLMProvider, VisionProvider):
    """Claude vía API de Anthropic, con tool-use nativo (ADR-007).

    - Reintenta SOLO ante 429, con backoff exponencial que respeta `retry-after`
      hasta `retry_after_cap_seconds`. Al agotar reintentos lanza `RateLimitError`.
    - El SDK se construye con `max_retries=0`: los reintentos son nuestros.
    - Los nombres de modelo llegan por `model_map`; los precios por `pricing`
      (USD por millón de tokens). Nada de eso está hardcodeado aquí.
    """

    _TIERS = (ModelTier.FAST, ModelTier.SMART, ModelTier.VISION)

    def __init__(
        self,
        api_key: SecretStr,
        model_map: Mapping[ModelTier, str],
        *,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_after_cap_seconds: float = 30.0,
        pricing: Mapping[str, ModelPricing] | None = None,
        client: anthropic.AsyncAnthropic | None = None,
        sleep: SleepFn = asyncio.sleep,
    ) -> None:
        faltantes = [t for t in self._TIERS if t not in model_map]
        if faltantes:
            raise ValueError(
                f"model_map debe definir un modelo para los tiers: {[t.value for t in faltantes]}"
            )
        self._model_map = {t: model_map[t] for t in self._TIERS}
        self._max_retries = max_retries
        self._retry_after_cap = retry_after_cap_seconds
        self._pricing = dict(pricing or {})
        self._sleep = sleep
        self._client = client or anthropic.AsyncAnthropic(
            api_key=api_key.get_secret_value(),
            timeout=timeout,
            max_retries=0,
        )

    @classmethod
    def from_settings(cls, settings: Settings) -> AnthropicProvider:
        """Construye el provider desde `Settings` (única fuente de modelos y precios)."""
        if settings.ANTHROPIC_API_KEY is None:
            raise ValueError("ANTHROPIC_API_KEY no está configurada.")
        return cls(
            api_key=settings.ANTHROPIC_API_KEY,
            model_map={
                ModelTier.FAST: settings.ANTHROPIC_MODEL_FAST,
                ModelTier.SMART: settings.ANTHROPIC_MODEL_SMART,
                ModelTier.VISION: settings.ANTHROPIC_MODEL_VISION,
            },
            timeout=settings.ANTHROPIC_TIMEOUT_SECONDS,
            max_retries=settings.ANTHROPIC_MAX_RETRIES,
            retry_after_cap_seconds=settings.ANTHROPIC_RETRY_AFTER_CAP_SECONDS,
            pricing=settings.ANTHROPIC_PRICING,
        )

    # ------------------------------------------------------------------ props

    @property
    def name(self) -> str:
        return PROVIDER_NAME

    @property
    def supported_tiers(self) -> list[ModelTier]:
        return list(self._TIERS)

    @property
    def supports_tools(self) -> bool:
        return True

    # ------------------------------------------------------------- public API

    async def complete(
        self,
        request: CompletionRequest,
        tier: ModelTier = ModelTier.SMART,
    ) -> CompletionResponse:
        """Genera una respuesta completa con Claude.

        Excepción explícita al contrato de `CompletionRequest`: `temperature` NO
        se envía. Los modelos vigentes de Anthropic rechazan los parámetros de
        muestreo con HTTP 400, así que se ignora en vez de romper cada request.
        También se desactiva el thinking: nuestra interface no conserva los
        bloques `thinking` entre `complete()` y `continue_with_tool_results()`,
        y reenviar un turno de tool-use sin ellos no es válido con thinking activo.

        Con `json_mode=True` se refuerza la instrucción en el system prompt y la
        respuesta se valida con `json.loads`; si no es JSON válido lanza
        `InvalidResponseError` (nunca se devuelve basura como respuesta válida).

        Excepción explícita a "`content` es lo que dijo el modelo": los modelos
        suelen envolver el JSON en un bloque markdown (```json ... ```) aun
        cuando se les pide que no. En `json_mode`, si TODO el texto (tras
        `strip`) es un único fence de apertura con etiqueta de lenguaje opcional
        y cierre, se quita el fence y `content` trae el JSON ya sin él. No se
        extrae JSON de texto con prosa alrededor, ni de un fence sin cerrar:
        ambos casos lanzan `InvalidResponseError`.
        """
        self._reject_tools_if_unsupported(request)
        return await self._run(request, tier, extra_messages=[])

    async def stream(
        self,
        request: CompletionRequest,
        tier: ModelTier = ModelTier.SMART,
    ) -> AsyncIterator[str]:
        """Emite el texto de la respuesta progresivamente.

        Un 429 solo se reintenta si ocurre antes del primer chunk; una vez que
        se emitió texto, reintentar duplicaría contenido al usuario.
        """
        self._reject_tools_if_unsupported(request)
        params = helpers.build_request_params(request, self._model_for(tier))
        attempt = 0
        while True:
            emitted = False
            try:
                async with self._client.messages.stream(**params) as stream:
                    async for chunk in stream.text_stream:
                        emitted = True
                        yield chunk
                return
            except anthropic.RateLimitError as exc:
                if emitted or attempt >= self._max_retries:
                    raise self._rate_limit_error() from exc
                await self._backoff(attempt, exc)
                attempt += 1
            except anthropic.APIError as exc:
                raise self._map_error(exc) from exc

    async def continue_with_tool_results(
        self,
        original_request: CompletionRequest,
        tool_calls: list[ToolCall],
        tool_results: list[ToolResult],
        tier: ModelTier = ModelTier.SMART,
    ) -> CompletionResponse:
        """Reenvía los resultados de tools para que Claude redacte la respuesta final."""
        self._reject_tools_if_unsupported(original_request)
        extra = helpers.build_tool_turn_messages(tool_calls, tool_results)
        return await self._run(original_request, tier, extra_messages=extra)

    async def analyze_image(self, image_bytes: bytes, prompt: str) -> str:
        """Describe/analiza una imagen con el tier VISION."""
        model = self._model_for(ModelTier.VISION)
        params = helpers.build_image_params(model, image_bytes, prompt)
        started = time.perf_counter()
        message = await self._create_with_retries(params)
        latency_ms = int((time.perf_counter() - started) * 1000)
        cost = helpers.compute_cost(
            self._pricing, model, message.usage.input_tokens, message.usage.output_tokens
        )
        self._log_usage(model, message, latency_ms=latency_ms, cost=cost, operation="analyze_image")
        return "".join(b.text for b in message.content if b.type == "text")

    async def health_check(self) -> bool:
        """Verifica que la API key y el modelo SMART sean válidos, sin gastar tokens."""
        model = self._model_for(ModelTier.SMART)
        try:
            await self._client.models.retrieve(model)
        except anthropic.RateLimitError:
            return True  # 429 implica que la key es válida y el servicio responde.
        except anthropic.APIError as exc:
            logger.warning("anthropic_health_check_failed", error_type=type(exc).__name__)
            return False
        return True

    # --------------------------------------------------------------- internals

    def _model_for(self, tier: ModelTier) -> str:
        try:
            return self._model_map[tier]
        except KeyError:
            raise UnsupportedTierError(
                f"AnthropicProvider no atiende el tier '{tier.value}' "
                f"(soporta: {[t.value for t in self._TIERS]})."
            ) from None

    async def _run(
        self,
        request: CompletionRequest,
        tier: ModelTier,
        *,
        extra_messages: list[dict[str, Any]],
    ) -> CompletionResponse:
        model = self._model_for(tier)
        params = helpers.build_request_params(request, model, extra_messages)
        started = time.perf_counter()
        message = await self._create_with_retries(params)
        latency_ms = int((time.perf_counter() - started) * 1000)

        if message.stop_reason == "refusal":
            raise ContentFilterError("Claude rechazó el request por su filtro de seguridad.")

        text = "".join(b.text for b in message.content if b.type == "text")
        tool_calls = [
            ToolCall(
                id=b.id, name=b.name, arguments=dict(b.input) if isinstance(b.input, dict) else {}
            )
            for b in message.content
            if b.type == "tool_use"
        ]
        if request.json_mode and not tool_calls:
            text = helpers.unwrap_and_validate_json(text)

        cost = helpers.compute_cost(
            self._pricing, model, message.usage.input_tokens, message.usage.output_tokens
        )
        self._log_usage(model, message, latency_ms=latency_ms, cost=cost, operation="complete")
        return CompletionResponse(
            content=text,
            tokens_input=message.usage.input_tokens,
            tokens_output=message.usage.output_tokens,
            model_used=message.model,
            provider=PROVIDER_NAME,
            latency_ms=latency_ms,
            cost_usd=cost,
            tool_calls=tool_calls or None,
            stop_reason=helpers.map_stop_reason(message.stop_reason),
        )

    async def _create_with_retries(self, params: dict[str, Any]) -> anthropic.types.Message:
        attempt = 0
        while True:
            try:
                message: anthropic.types.Message = await self._client.messages.create(**params)
                return message
            except anthropic.RateLimitError as exc:
                if attempt >= self._max_retries:
                    raise self._rate_limit_error() from exc
                await self._backoff(attempt, exc)
                attempt += 1
            except anthropic.APIError as exc:
                raise self._map_error(exc) from exc

    async def _backoff(self, attempt: int, exc: anthropic.RateLimitError) -> None:
        delay = helpers.retry_delay(
            exc.response.headers.get("retry-after"), attempt, self._retry_after_cap
        )
        logger.warning("anthropic_rate_limited", attempt=attempt + 1, sleep_seconds=round(delay, 2))
        await self._sleep(delay)

    @staticmethod
    def _rate_limit_error() -> RateLimitError:
        return RateLimitError(
            "Anthropic rechazó el request por límite de tasa (reintentos agotados)."
        )

    @staticmethod
    def _map_error(exc: anthropic.APIError) -> AIProviderError:
        """Traduce errores del SDK a las excepciones agnósticas de la capa de IA."""
        logger.error(
            "anthropic_api_error",
            error_type=type(exc).__name__,
            status_code=getattr(exc, "status_code", None),
        )
        # Errores de request (400/404/422/413/409) son bug nuestro: NO son "proveedor
        # caído", así que no deben disparar fallback silencioso en el router.
        if isinstance(
            exc,
            anthropic.BadRequestError
            | anthropic.NotFoundError
            | anthropic.UnprocessableEntityError
            | anthropic.RequestTooLargeError
            | anthropic.ConflictError,
        ):
            return AIProviderError(f"Anthropic rechazó el request: {type(exc).__name__}.")
        # Auth, permisos, 5xx, sobrecarga, timeout y red: el proveedor no está disponible.
        return ProviderUnavailableError(f"Anthropic no disponible: {type(exc).__name__}.")

    @staticmethod
    def _log_usage(
        model: str,
        message: anthropic.types.Message,
        *,
        latency_ms: int,
        cost: float | None,
        operation: str,
    ) -> None:
        # Nunca contenido del usuario ni credenciales: solo métricas.
        logger.info(
            "anthropic_request",
            operation=operation,
            model=model,
            tokens_input=message.usage.input_tokens,
            tokens_output=message.usage.output_tokens,
            latency_ms=latency_ms,
            cost_usd=cost,
        )
