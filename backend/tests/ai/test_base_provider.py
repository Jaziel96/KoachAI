"""Tests de US-006: interface base de proveedores de IA.

Cubre CA-1, CA-2, CA-4, CA-5. CA-3 (mypy strict) se valida vía
`mypy app` en CI/lint, no como test de pytest.
"""

from __future__ import annotations

import pytest

from app.ai.exceptions import ToolsNotSupportedError
from app.ai.providers.base_provider import (
    CompletionRequest,
    Message,
    ModelTier,
    StopReason,
    ToolDefinition,
)
from tests.ai.providers.fake_tool_provider import FakeNoToolsProvider, FakeToolProvider
from tests.ai.providers.mock_provider import MockLLMProvider


def test_ca1_base_provider_no_importa_sdks_de_proveedores() -> None:
    """CA-1: `LLMProvider` no importa `anthropic` ni `google.generativeai`."""
    import ast

    import app.ai.providers.base_provider as module

    source = module.__file__
    assert source is not None
    with open(source, encoding="utf-8") as f:
        arbol = ast.parse(f.read(), filename=source)

    sdks_prohibidos = {"anthropic", "google", "google.generativeai", "openai"}
    modulos_importados: set[str] = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            modulos_importados.update(alias.name for alias in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            modulos_importados.add(nodo.module)

    # El AST prueba CA-1 sin depender de `sys.modules`, que es estado global del
    # proceso: otro test (p. ej. AnthropicProvider, US-007) puede importar el SDK.
    assert modulos_importados.isdisjoint(sdks_prohibidos)


@pytest.mark.asyncio
async def test_ca2_provider_ficticio_implementa_las_tres_interfaces() -> None:
    """CA-2: se puede crear un provider ficticio implementando la interface."""
    provider = MockLLMProvider()

    request = CompletionRequest(messages=[Message(role="user", content="hola")])
    response = await provider.complete(request)
    assert response.content == "respuesta mock"

    chunks = [chunk async for chunk in provider.stream(request)]
    assert chunks == ["respuesta mock"]

    assert await provider.health_check() is True
    assert await provider.transcribe(b"audio") == "transcripción mock"
    assert await provider.analyze_image(b"imagen", "describe") == "análisis mock"


@pytest.mark.asyncio
async def test_ca4_request_con_tools_retorna_tool_calls() -> None:
    """CA-4 (verificación de contrato — ver docstring de FakeToolProvider).

    Un `CompletionRequest` con `tools` no vacío, contra un provider que
    soporta tool-use, retorna `tool_calls` con `stop_reason=TOOL_USE` cuando
    el modelo decide usar una herramienta. Repetir contra `AnthropicProvider`
    real en US-007.
    """
    provider = FakeToolProvider()
    tool = ToolDefinition(
        name="registrar_peso",
        description="Registra el peso actual del usuario",
        input_schema={"type": "object", "properties": {"kg": {"type": "number"}}},
    )
    request = CompletionRequest(
        messages=[Message(role="user", content="ya me pesé, 80kg")],
        tools=[tool],
    )

    response = await provider.complete(request, tier=ModelTier.SMART)

    assert response.stop_reason == StopReason.TOOL_USE
    assert response.tool_calls is not None
    assert len(response.tool_calls) == 1
    assert response.tool_calls[0].name == "registrar_peso"


@pytest.mark.asyncio
async def test_ca4_sin_tools_no_hay_tool_calls() -> None:
    provider = FakeToolProvider()
    request = CompletionRequest(messages=[Message(role="user", content="hola")])

    response = await provider.complete(request)

    assert response.stop_reason == StopReason.END_TURN
    assert response.tool_calls is None


@pytest.mark.asyncio
async def test_ca5_provider_sin_soporte_de_tools_rechaza_request_con_tools() -> None:
    """CA-5: provider con `supports_tools=False` lanza excepción clara, no ignora `tools`."""
    provider = FakeNoToolsProvider()
    tool = ToolDefinition(name="x", description="x", input_schema={})
    request = CompletionRequest(
        messages=[Message(role="user", content="hola")],
        tools=[tool],
    )

    with pytest.raises(ToolsNotSupportedError):
        await provider.complete(request)


@pytest.mark.asyncio
async def test_ca5_provider_sin_soporte_de_tools_acepta_request_sin_tools() -> None:
    provider = FakeNoToolsProvider()
    request = CompletionRequest(messages=[Message(role="user", content="hola")])

    response = await provider.complete(request)

    assert response.content == "respuesta sin soporte de tools"


@pytest.mark.asyncio
async def test_continue_with_tool_results_redacta_respuesta_final() -> None:
    """RF-12: forma estándar de reenviar resultados de tools para la respuesta final."""
    from app.ai.providers.base_provider import ToolCall, ToolResult

    provider = FakeToolProvider()
    original_request = CompletionRequest(messages=[Message(role="user", content="ya me pesé")])
    tool_calls = [ToolCall(id="call_fake_1", name="registrar_peso", arguments={"kg": 80})]
    tool_results = [
        ToolResult(tool_call_id="call_fake_1", content="peso registrado: 80kg", is_error=False)
    ]

    response = await provider.continue_with_tool_results(
        original_request, tool_calls, tool_results
    )

    assert response.stop_reason == StopReason.END_TURN
    assert "peso registrado: 80kg" in response.content
