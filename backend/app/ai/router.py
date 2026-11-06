"""Router de IA — punto único de entrada a la capa de IA (US-009, ADR-007).

Selecciona el proveedor adecuado por `ModelTier`, respeta qué proveedores
soportan tool-use (RF-6/RF-7), hace fallback ante caídas o rate limits
(RF-3), y registra métricas de uso en logs estructurados (RF-5/RF-8) — nunca
contenido del usuario ni de la respuesta.

Hoy solo hay un proveedor registrado (Anthropic: Haiku en FAST, Sonnet en
SMART/VISION — ver ADR de alcance en CLAUDE.md/.env.example). El diseño ya
soporta cadenas de varios proveedores por tier; agregar un segundo proveedor
real es solo registrarlo en `from_settings()` y extender la cadena, sin
tocar `complete()`/`stream()`.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from app.ai.exceptions import ProviderUnavailableError, RateLimitError
from app.ai.providers.anthropic_provider import AnthropicProvider
from app.ai.providers.base_provider import (
    CompletionRequest,
    CompletionResponse,
    LLMProvider,
    ModelTier,
    ToolCall,
    ToolResult,
)
from app.core.config import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Errores que indican que ESTE proveedor no pudo atender el request, pero que
# otro sí podría (caída, timeout, límite de tasa): disparan fallback al
# siguiente candidato de la cadena (RF-3).
#
# Cualquier otro error (ContentFilterError, UnsupportedTierError,
# InvalidResponseError, ToolsNotSupportedError) NO dispara fallback: son del
# contenido o de una llamada mal construida, no de disponibilidad, y
# esconderlos reintentando en otro proveedor ocultaría el problema real en
# vez de resolverlo (p. ej. un bloqueo de contenido no desaparece por
# cambiar de proveedor).
_FALLBACK_WORTHY: tuple[type[Exception], ...] = (ProviderUnavailableError, RateLimitError)


def _resumen_errores(candidatos: list[LLMProvider], errores: list[Exception]) -> str:
    """Arma "proveedor (TipoDeError)" por cada intento fallido, para el mensaje final."""
    return ", ".join(
        f"{c.name} ({type(e).__name__})" for c, e in zip(candidatos, errores, strict=True)
    )


def _build_provider_registry(settings: Settings) -> dict[str, LLMProvider]:
    """Construye el registro de proveedores disponibles según configuración.

    Solo registra un proveedor si tiene credenciales — sin API key, ese
    proveedor simplemente no aparece en el registro, y cualquier tier que
    dependa de él falla con un `ProviderUnavailableError` claro en vez de un
    error de construcción confuso.
    """
    providers: dict[str, LLMProvider] = {}
    if settings.ANTHROPIC_API_KEY is not None:
        anthropic_provider = AnthropicProvider.from_settings(settings)
        providers[anthropic_provider.name] = anthropic_provider
    return providers


def _build_tier_chains(settings: Settings) -> dict[ModelTier, list[str]]:
    """Cadena de nombres de proveedor por tier, en orden de preferencia.

    Hoy cada cadena tiene un único nombre (un solo proveedor configurado por
    tier) — RF-3 (fallback) se activa automáticamente el día que haya un
    segundo proveedor registrado para el mismo tier, sin cambiar esta
    función más que agregarlo a la lista.

    VISION se enruta al mismo proveedor que SMART: no hay una variable
    `AI_VISION_PROVIDER` separada en `Settings` hoy, y `AnthropicProvider` ya
    implementa `VisionProvider` usando el modelo configurado en
    `ANTHROPIC_MODEL_VISION`. AUDIO no tiene proveedor configurado — ningún
    proveedor de `complete()`/`stream()` sirve transcripción (es la interface
    `TranscriptionProvider`, aparte); pedir tier AUDIO aquí da un error claro.
    """
    return {
        ModelTier.FAST: [settings.AI_FAST_PROVIDER],
        ModelTier.SMART: [settings.AI_SMART_PROVIDER],
        ModelTier.VISION: [settings.AI_SMART_PROVIDER],
    }


class AIRouter:
    """Selecciona proveedor por tier, con fallback y métricas (US-009)."""

    def __init__(
        self,
        providers: dict[str, LLMProvider],
        tier_chains: dict[ModelTier, list[str]],
    ) -> None:
        self.providers = providers
        self.tier_chains = tier_chains

    @classmethod
    def from_settings(cls, settings: Settings) -> AIRouter:
        """Construye el router real desde `Settings` (RF-1).

        Solo la estrategia `"api"` tiene proveedores implementados hoy;
        `"hybrid"` y `"local"` existen en el contrato de configuración para
        cuando haya proveedores locales (ver sección 3.4 del SDD), pero
        fingir que funcionan hoy sería peor que fallar claro al arrancar.
        """
        if settings.AI_STRATEGY != "api":
            raise NotImplementedError(
                f"AI_STRATEGY={settings.AI_STRATEGY!r} aún no tiene proveedores "
                "implementados — solo 'api' (Anthropic) existe hoy."
            )
        return cls(
            providers=_build_provider_registry(settings),
            tier_chains=_build_tier_chains(settings),
        )

    def _candidates(self, tier: ModelTier, request: CompletionRequest) -> list[LLMProvider]:
        """Cadena de proveedores candidatos para este tier y request.

        Si `request.tools` no está vacío, filtra a los que soportan tool-use
        (RF-6/CA-5) ANTES de intentar nada — nunca se envía un request con
        tools a un proveedor que las ignoraría en silencio.
        """
        nombres = self.tier_chains.get(tier, [])
        candidatos = [self.providers[nombre] for nombre in nombres if nombre in self.providers]

        if request.tools:
            candidatos = [c for c in candidatos if c.supports_tools]
            if not candidatos:
                raise ProviderUnavailableError(
                    f"El request incluye tools, pero ningún proveedor disponible "
                    f"para el tier '{tier.value}' soporta tool-use (CA-6). "
                    "No se reintenta sin tools — el llamador decide qué hacer."
                )
            return candidatos

        if not candidatos:
            raise ProviderUnavailableError(
                f"No hay ningún proveedor configurado para el tier '{tier.value}'."
            )
        return candidatos

    def _log_success(
        self, *, tier: ModelTier, response: CompletionResponse, attempt_number: int
    ) -> None:
        tool_calls = response.tool_calls or []
        logger.info(
            "ai_router_complete",
            tier=tier.value,
            provider=response.provider,
            model_used=response.model_used,
            attempt_number=attempt_number,
            tokens_input=response.tokens_input,
            tokens_output=response.tokens_output,
            cost_usd=response.cost_usd,
            latency_ms=response.latency_ms,
            stop_reason=response.stop_reason.value,
            tool_calls_count=len(tool_calls),
            tool_call_names=[tc.name for tc in tool_calls],
        )

    def _log_failure(self, *, tier: ModelTier, provider_name: str, error: Exception) -> None:
        logger.warning(
            "ai_router_provider_failed",
            tier=tier.value,
            provider=provider_name,
            error_type=type(error).__name__,
        )

    async def complete(
        self,
        request: CompletionRequest,
        tier: ModelTier = ModelTier.SMART,
        *,
        prefer_local: bool = False,
    ) -> CompletionResponse:
        """Genera una respuesta completa, con fallback y métricas (RF-1 a RF-8).

        `prefer_local` (RF-4) queda reservado para cuando exista algún
        proveedor local: ningún `LLMProvider` de hoy se declara local, así
        que pedirlo en `True` no cambia el ruteo — solo se registra en el log
        para no fingir un comportamiento que no existe todavía.
        """
        if prefer_local:
            logger.info(
                "ai_router_prefer_local_ignorado",
                tier=tier.value,
                motivo="no hay proveedores locales configurados",
            )

        candidatos = self._candidates(tier, request)
        errores: list[Exception] = []

        for intento, candidato in enumerate(candidatos, start=1):
            try:
                respuesta = await candidato.complete(request, tier=tier)
            except _FALLBACK_WORTHY as exc:
                self._log_failure(tier=tier, provider_name=candidato.name, error=exc)
                errores.append(exc)
                continue
            self._log_success(tier=tier, response=respuesta, attempt_number=intento)
            return respuesta

        raise ProviderUnavailableError(
            f"Todos los proveedores para el tier '{tier.value}' fallaron: "
            f"{_resumen_errores(candidatos, errores)}"
        )

    async def stream(
        self,
        request: CompletionRequest,
        tier: ModelTier = ModelTier.SMART,
    ) -> AsyncIterator[str]:
        """Genera respuesta en streaming, con la misma selección de proveedor.

        Sin fallback a mitad de stream: si el proveedor falla después de
        haber emitido texto, reintentar en otro proveedor duplicaría
        contenido ya enviado al usuario. Solo se reintenta antes de emitir
        el primer chunk.

        Nota: la interface de streaming no retorna un `CompletionResponse`
        final, así que a diferencia de `complete()` no se registran métricas
        de tokens/costo aquí — ver limitación documentada, no se inventan.
        """
        candidatos = self._candidates(tier, request)
        errores: list[Exception] = []

        for candidato in candidatos:
            try:
                primer_chunk: str | None = None
                generador = candidato.stream(request, tier=tier)
                async for chunk in generador:
                    if primer_chunk is None:
                        primer_chunk = chunk
                        logger.info(
                            "ai_router_stream_started", tier=tier.value, provider=candidato.name
                        )
                    yield chunk
                return
            except _FALLBACK_WORTHY as exc:
                self._log_failure(tier=tier, provider_name=candidato.name, error=exc)
                errores.append(exc)
                continue

        raise ProviderUnavailableError(
            f"Todos los proveedores para el tier '{tier.value}' fallaron en stream(): "
            f"{_resumen_errores(candidatos, errores)}"
        )

    async def continue_with_tool_results(
        self,
        provider_name: str,
        original_request: CompletionRequest,
        tool_calls: list[ToolCall],
        tool_results: list[ToolResult],
        tier: ModelTier = ModelTier.SMART,
    ) -> CompletionResponse:
        """Reenvía resultados de tools al proveedor que las generó (RF-12).

        No hay selección ni fallback aquí: los `tool_calls` originales (IDs,
        formato) son específicos del proveedor que los produjo — continuar
        la conversación contra un proveedor distinto no es válido. El
        llamador pasa `provider_name=response.provider` de la respuesta
        original de `complete()`.
        """
        proveedor = self.providers.get(provider_name)
        if proveedor is None:
            raise ProviderUnavailableError(
                f"Proveedor '{provider_name}' inexistente o no registrado — no se puede "
                "continuar un ciclo de tools contra un proveedor distinto al que las generó."
            )

        respuesta = await proveedor.continue_with_tool_results(
            original_request, tool_calls, tool_results, tier=tier
        )
        self._log_success(tier=tier, response=respuesta, attempt_number=1)
        return respuesta
