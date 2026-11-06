"""Tests de US-009: AIRouter.

Cubre CA-1 a CA-7. Usa providers ficticios locales (no AnthropicProvider real)
para poder simular caídas, tiers no soportados y fallback de forma
determinista — CA-2 (fallback) necesita al menos dos proveedores, y hoy en
producción solo hay uno (Anthropic); con fakes se prueba que la selección
funciona, lista para cuando se registre un segundo proveedor real.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

import pytest
import structlog
import structlog.testing

from app.ai.exceptions import (
    ContentFilterError,
    ProviderUnavailableError,
    RateLimitError,
)
from app.ai.providers.base_provider import (
    CompletionRequest,
    CompletionResponse,
    LLMProvider,
    Message,
    ModelTier,
    StopReason,
    ToolCall,
    ToolDefinition,
    ToolResult,
)
from app.ai.router import AIRouter


class _FakeProvider(LLMProvider):
    """Provider ficticio configurable: puede fallar en `complete()` a demanda."""

    def __init__(
        self,
        name: str,
        *,
        tiers: list[ModelTier] | None = None,
        supports_tools: bool = True,
        fail_with: Exception | None = None,
    ) -> None:
        self._name = name
        self._tiers = tiers or [ModelTier.FAST, ModelTier.SMART, ModelTier.VISION]
        self._supports_tools = supports_tools
        self._fail_with = fail_with
        self.calls: list[CompletionRequest] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def supported_tiers(self) -> list[ModelTier]:
        return self._tiers

    @property
    def supports_tools(self) -> bool:
        return self._supports_tools

    async def complete(
        self, request: CompletionRequest, tier: ModelTier = ModelTier.SMART
    ) -> CompletionResponse:
        self._reject_tools_if_unsupported(request)
        self.calls.append(request)
        if self._fail_with is not None:
            raise self._fail_with
        tool_calls = (
            [ToolCall(id="call_1", name="obtener_clima", arguments={})]
            if request.tools
            else None
        )
        return CompletionResponse(
            content="ok",
            tokens_input=10,
            tokens_output=5,
            model_used=f"{self._name}-model",
            provider=self._name,
            latency_ms=42,
            cost_usd=0.001,
            tool_calls=tool_calls,
            stop_reason=StopReason.TOOL_USE if tool_calls else StopReason.END_TURN,
        )

    async def stream(
        self, request: CompletionRequest, tier: ModelTier = ModelTier.SMART
    ) -> AsyncIterator[str]:
        self._reject_tools_if_unsupported(request)
        if self._fail_with is not None:
            raise self._fail_with
        yield "chunk-1"
        yield "chunk-2"

    async def continue_with_tool_results(
        self,
        original_request: CompletionRequest,
        tool_calls: list[ToolCall],
        tool_results: list[ToolResult],
        tier: ModelTier = ModelTier.SMART,
    ) -> CompletionResponse:
        return CompletionResponse(
            content="respuesta final",
            tokens_input=5,
            tokens_output=5,
            model_used=f"{self._name}-model",
            provider=self._name,
            latency_ms=10,
            stop_reason=StopReason.END_TURN,
        )

    async def health_check(self) -> bool:
        return self._fail_with is None


def _request(*, tools: list[ToolDefinition] | None = None) -> CompletionRequest:
    return CompletionRequest(messages=[Message(role="user", content="hola")], tools=tools)


_TOOL = ToolDefinition(name="obtener_clima", description="clima", input_schema={})


# --- CA-1 / CA-3: selección por tier y por config ---


@pytest.mark.asyncio
async def test_ca1_rutea_por_tier_segun_configuracion() -> None:
    fast = _FakeProvider("fast-provider")
    smart = _FakeProvider("smart-provider")
    router = AIRouter(
        providers={"fast-provider": fast, "smart-provider": smart},
        tier_chains={ModelTier.FAST: ["fast-provider"], ModelTier.SMART: ["smart-provider"]},
    )

    resultado_fast = await router.complete(_request(), tier=ModelTier.FAST)
    resultado_smart = await router.complete(_request(), tier=ModelTier.SMART)

    assert resultado_fast.provider == "fast-provider"
    assert resultado_smart.provider == "smart-provider"


@pytest.mark.asyncio
async def test_ca3_cambiar_config_cambia_el_ruteo() -> None:
    a = _FakeProvider("a")
    b = _FakeProvider("b")
    router_con_a = AIRouter(providers={"a": a, "b": b}, tier_chains={ModelTier.SMART: ["a"]})
    router_con_b = AIRouter(providers={"a": a, "b": b}, tier_chains={ModelTier.SMART: ["b"]})

    resultado_a = await router_con_a.complete(_request(), tier=ModelTier.SMART)
    resultado_b = await router_con_b.complete(_request(), tier=ModelTier.SMART)

    assert resultado_a.provider == "a"
    assert resultado_b.provider == "b"


def test_sin_cadena_configurada_para_el_tier_lanza_error_claro() -> None:
    router = AIRouter(providers={}, tier_chains={})

    with pytest.raises(ProviderUnavailableError, match="audio"):
        import asyncio

        asyncio.run(router.complete(_request(), tier=ModelTier.AUDIO))


# --- CA-2: fallback ante proveedor caído ---


@pytest.mark.asyncio
async def test_ca2_fallback_al_segundo_proveedor_si_el_primero_cae() -> None:
    caido = _FakeProvider("caido", fail_with=ProviderUnavailableError("timeout"))
    sano = _FakeProvider("sano")
    router = AIRouter(
        providers={"caido": caido, "sano": sano},
        tier_chains={ModelTier.SMART: ["caido", "sano"]},
    )

    resultado = await router.complete(_request(), tier=ModelTier.SMART)

    assert resultado.provider == "sano"


@pytest.mark.asyncio
async def test_fallback_tambien_ante_rate_limit() -> None:
    limitado = _FakeProvider("limitado", fail_with=RateLimitError("429"))
    sano = _FakeProvider("sano")
    router = AIRouter(
        providers={"limitado": limitado, "sano": sano},
        tier_chains={ModelTier.SMART: ["limitado", "sano"]},
    )

    resultado = await router.complete(_request(), tier=ModelTier.SMART)

    assert resultado.provider == "sano"


@pytest.mark.asyncio
async def test_error_de_contenido_no_dispara_fallback() -> None:
    """Un ContentFilterError es del contenido, no del proveedor: no debe
    reintentarse contra otro proveedor (eso solo escondería el bloqueo)."""
    bloqueado = _FakeProvider("bloqueado", fail_with=ContentFilterError("bloqueado"))
    otro = _FakeProvider("otro")
    router = AIRouter(
        providers={"bloqueado": bloqueado, "otro": otro},
        tier_chains={ModelTier.SMART: ["bloqueado", "otro"]},
    )

    with pytest.raises(ContentFilterError):
        await router.complete(_request(), tier=ModelTier.SMART)

    assert otro.calls == []


@pytest.mark.asyncio
async def test_si_se_agota_la_cadena_lanza_provider_unavailable_explicito() -> None:
    a = _FakeProvider("a", fail_with=ProviderUnavailableError("caído"))
    b = _FakeProvider("b", fail_with=ProviderUnavailableError("también caído"))
    router = AIRouter(providers={"a": a, "b": b}, tier_chains={ModelTier.SMART: ["a", "b"]})

    with pytest.raises(ProviderUnavailableError):
        await router.complete(_request(), tier=ModelTier.SMART)


# --- CA-5 / CA-6: tools ---


@pytest.mark.asyncio
async def test_ca5_request_con_tools_nunca_va_a_proveedor_sin_soporte() -> None:
    sin_tools = _FakeProvider("sin-tools", supports_tools=False)
    con_tools = _FakeProvider("con-tools", supports_tools=True)
    router = AIRouter(
        providers={"sin-tools": sin_tools, "con-tools": con_tools},
        tier_chains={ModelTier.SMART: ["sin-tools", "con-tools"]},
    )

    resultado = await router.complete(_request(tools=[_TOOL]), tier=ModelTier.SMART)

    assert resultado.provider == "con-tools"
    assert sin_tools.calls == []


@pytest.mark.asyncio
async def test_ca6_sin_ningun_proveedor_con_tools_lanza_error_explicito() -> None:
    sin_tools_1 = _FakeProvider("sin-tools-1", supports_tools=False)
    sin_tools_2 = _FakeProvider("sin-tools-2", supports_tools=False)
    router = AIRouter(
        providers={"sin-tools-1": sin_tools_1, "sin-tools-2": sin_tools_2},
        tier_chains={ModelTier.SMART: ["sin-tools-1", "sin-tools-2"]},
    )

    with pytest.raises(ProviderUnavailableError, match="tools"):
        await router.complete(_request(tools=[_TOOL]), tier=ModelTier.SMART)

    assert sin_tools_1.calls == []
    assert sin_tools_2.calls == []


@pytest.mark.asyncio
async def test_tools_hace_fallback_solo_a_proveedores_que_tambien_las_soportan() -> None:
    con_tools_caido = _FakeProvider(
        "con-tools-caido", supports_tools=True, fail_with=ProviderUnavailableError("caído")
    )
    sin_tools_sano = _FakeProvider("sin-tools-sano", supports_tools=False)
    router = AIRouter(
        providers={"con-tools-caido": con_tools_caido, "sin-tools-sano": sin_tools_sano},
        tier_chains={ModelTier.SMART: ["con-tools-caido", "sin-tools-sano"]},
    )

    with pytest.raises(ProviderUnavailableError):
        await router.complete(_request(tools=[_TOOL]), tier=ModelTier.SMART)

    assert sin_tools_sano.calls == []


# --- CA-4 / CA-7: métricas en logs ---


@pytest.mark.asyncio
async def test_ca4_ca7_metricas_y_tool_calls_quedan_en_el_log() -> None:
    provider = _FakeProvider("x")
    router = AIRouter(providers={"x": provider}, tier_chains={ModelTier.SMART: ["x"]})

    with structlog.testing.capture_logs() as logs:
        await router.complete(_request(tools=[_TOOL]), tier=ModelTier.SMART)

    eventos = [log for log in logs if log.get("event") == "ai_router_complete"]
    assert len(eventos) == 1
    evento = eventos[0]
    assert evento["provider"] == "x"
    assert evento["tier"] == "smart"
    assert evento["tokens_input"] == 10
    assert evento["tokens_output"] == 5
    assert evento["cost_usd"] == 0.001
    assert evento["latency_ms"] == 42
    assert evento["tool_calls_count"] == 1
    assert evento["tool_call_names"] == ["obtener_clima"]
    # Nunca el contenido del usuario ni del modelo en el log de métricas.
    assert "content" not in evento
    assert "hola" not in str(evento)


@pytest.mark.asyncio
async def test_log_de_fallback_no_incluye_contenido_del_usuario() -> None:
    caido = _FakeProvider("caido", fail_with=ProviderUnavailableError("timeout"))
    sano = _FakeProvider("sano")
    router = AIRouter(
        providers={"caido": caido, "sano": sano},
        tier_chains={ModelTier.SMART: ["caido", "sano"]},
    )

    with structlog.testing.capture_logs() as logs:
        await router.complete(_request(), tier=ModelTier.SMART)

    fallos = [log for log in logs if log.get("event") == "ai_router_provider_failed"]
    assert len(fallos) == 1
    assert fallos[0]["provider"] == "caido"
    assert "hola" not in str(fallos[0])


# --- stream() y continue_with_tool_results() siguen la misma selección ---


@pytest.mark.asyncio
async def test_stream_usa_la_misma_seleccion_de_proveedor() -> None:
    sano = _FakeProvider("sano")
    router = AIRouter(providers={"sano": sano}, tier_chains={ModelTier.SMART: ["sano"]})

    chunks = [c async for c in router.stream(_request(), tier=ModelTier.SMART)]

    assert chunks == ["chunk-1", "chunk-2"]


@pytest.mark.asyncio
async def test_continue_with_tool_results_va_al_proveedor_que_genero_los_tool_calls() -> None:
    a = _FakeProvider("a")
    b = _FakeProvider("b")
    router = AIRouter(providers={"a": a, "b": b}, tier_chains={ModelTier.SMART: ["a", "b"]})

    resultado = await router.continue_with_tool_results(
        provider_name="b",
        original_request=_request(tools=[_TOOL]),
        tool_calls=[ToolCall(id="call_1", name="obtener_clima", arguments={})],
        tool_results=[ToolResult(tool_call_id="call_1", content="25°C")],
        tier=ModelTier.SMART,
    )

    assert resultado.provider == "b"


@pytest.mark.asyncio
async def test_continue_with_tool_results_con_proveedor_desconocido_lanza_error_claro() -> None:
    a = _FakeProvider("a")
    router = AIRouter(providers={"a": a}, tier_chains={ModelTier.SMART: ["a"]})

    with pytest.raises(ProviderUnavailableError, match="inexistente"):
        await router.continue_with_tool_results(
            provider_name="inexistente",
            original_request=_request(),
            tool_calls=[],
            tool_results=[],
            tier=ModelTier.SMART,
        )


# --- RF-4: prefer_local (futuro, sin proveedor local hoy) ---


@pytest.mark.asyncio
async def test_prefer_local_sin_proveedor_local_no_rompe_y_usa_el_normal() -> None:
    sano = _FakeProvider("sano")
    router = AIRouter(providers={"sano": sano}, tier_chains={ModelTier.SMART: ["sano"]})

    resultado = await router.complete(_request(), tier=ModelTier.SMART, prefer_local=True)

    assert resultado.provider == "sano"


# --- from_settings: construcción real desde configuración ---


def _settings(**overrides: Any) -> Any:
    from pydantic import SecretStr

    from app.core.config import Settings

    base: dict[str, Any] = {
        "DATABASE_URL": "postgresql+asyncpg://user:password@localhost:5432/koach_test",
        "SUPABASE_URL": "https://example.supabase.co",
        "SUPABASE_SERVICE_KEY": "test-service-key",
        "REDIS_URL": "redis://localhost:6379/0",
        "WHATSAPP_TOKEN": "test-token",
        "WHATSAPP_PHONE_NUMBER_ID": "123456",
        "WHATSAPP_VERIFY_TOKEN": "test-verify-token",
        "ANTHROPIC_API_KEY": SecretStr("sk-ant-test-key"),
    }
    base.update(overrides)
    return Settings(**base)


def test_from_settings_registra_anthropic_si_hay_api_key() -> None:
    router = AIRouter.from_settings(_settings())

    assert "anthropic" in router.providers
    assert router.providers["anthropic"].name == "anthropic"


def test_from_settings_respeta_ai_smart_provider_y_ai_fast_provider() -> None:
    router = AIRouter.from_settings(
        _settings(AI_SMART_PROVIDER="anthropic", AI_FAST_PROVIDER="anthropic")
    )

    assert router.tier_chains[ModelTier.SMART] == ["anthropic"]
    assert router.tier_chains[ModelTier.FAST] == ["anthropic"]


def test_from_settings_sin_api_key_no_registra_el_proveedor() -> None:
    router = AIRouter.from_settings(_settings(ANTHROPIC_API_KEY=None))

    assert router.providers == {}


def test_from_settings_rechaza_estrategia_no_implementada() -> None:
    with pytest.raises(NotImplementedError, match="hybrid"):
        AIRouter.from_settings(_settings(AI_STRATEGY="hybrid"))
