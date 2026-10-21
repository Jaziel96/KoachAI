"""Integración de US-007 contra la API real de Anthropic.

Se omite si no hay `ANTHROPIC_API_KEY` real (en el entorno o en `backend/.env`).
Cubre el CA-4 heredado de US-006: un request con `tools` contra
`AnthropicProvider` retorna `tool_calls`. Cada test gasta centavos de dólar.

Ejecutar solo estos:  pytest -m integration -v
"""

from __future__ import annotations

import json
import struct
import zlib
from collections.abc import Iterator

import pytest
from pydantic import SecretStr

from app.ai.providers.anthropic_provider import AnthropicProvider
from app.ai.providers.base_provider import (
    CompletionRequest,
    Message,
    ModelTier,
    StopReason,
    ToolDefinition,
    ToolResult,
)
from app.core.config import get_settings

pytestmark = pytest.mark.integration

_PLACEHOLDER_KEYS = {"", "sk-ant-...", "sk-ant-"}


def _load_api_key() -> SecretStr | None:
    key = get_settings().ANTHROPIC_API_KEY
    if key is None or key.get_secret_value() in _PLACEHOLDER_KEYS:
        return None
    return key


# scope="function": cada test corre en su propio event loop (pytest-asyncio) y el
# cliente async no debe reutilizar conexiones ligadas a un loop ya cerrado.
@pytest.fixture
def provider() -> Iterator[AnthropicProvider]:
    if _load_api_key() is None:
        pytest.skip("Sin ANTHROPIC_API_KEY real: se omiten los tests de integración.")
    yield AnthropicProvider.from_settings(get_settings())


def _png_1x1() -> bytes:
    def chunk(tag: bytes, data: bytes) -> bytes:
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    idat = zlib.compress(b"\x00\xff\x00\x00")
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


_TOOL = ToolDefinition(
    name="registrar_agua",
    description="Registra los vasos de agua que el usuario dice haber tomado.",
    input_schema={
        "type": "object",
        "properties": {"vasos": {"type": "integer", "description": "Número de vasos"}},
        "required": ["vasos"],
    },
)


async def test_health_check_true_con_key_valida(provider: AnthropicProvider) -> None:
    assert await provider.health_check() is True


async def test_health_check_false_con_key_invalida() -> None:
    settings = get_settings()
    bogus = AnthropicProvider(
        api_key=SecretStr("clave-invalida-de-prueba"),
        model_map={
            ModelTier.FAST: settings.ANTHROPIC_MODEL_FAST,
            ModelTier.SMART: settings.ANTHROPIC_MODEL_SMART,
            ModelTier.VISION: settings.ANTHROPIC_MODEL_VISION,
        },
    )
    if _load_api_key() is None:
        pytest.skip("Sin ANTHROPIC_API_KEY real.")
    assert await bogus.health_check() is False


async def test_complete_real_y_sin_temperature(provider: AnthropicProvider) -> None:
    """Confirma que el modelo acepta el request sin `temperature` y con thinking desactivado."""
    request = CompletionRequest(
        messages=[Message(role="user", content="Responde solo con la palabra: listo")],
        max_tokens=50,
        temperature=0.2,  # se ignora a propósito; ver docstring de complete()
    )
    response = await provider.complete(request)
    assert "listo" in response.content.lower()
    assert response.tokens_input > 0
    assert response.tokens_output > 0
    assert response.stop_reason is StopReason.END_TURN
    assert response.provider == "anthropic"


async def test_stream_real_emite_chunks(provider: AnthropicProvider) -> None:
    request = CompletionRequest(
        messages=[Message(role="user", content="Cuenta del 1 al 5 separado por espacios")],
        max_tokens=100,
    )
    chunks = [c async for c in provider.stream(request)]
    assert len(chunks) >= 1
    assert "5" in "".join(chunks)


async def test_json_mode_real_devuelve_json_valido(provider: AnthropicProvider) -> None:
    request = CompletionRequest(
        messages=[Message(role="user", content="Dame un objeto con la clave 'fruta' y un valor.")],
        max_tokens=100,
        json_mode=True,
    )
    response = await provider.complete(request)
    assert isinstance(json.loads(response.content), dict)


async def test_tier_fast_json_mode_real(provider: AnthropicProvider) -> None:
    """FAST (Haiku) en modo JSON: extracción de datos, aceptado sin temperature."""
    request = CompletionRequest(
        messages=[
            Message(
                role="user",
                content="Extrae del texto: 'me comí 2 tacos de pastor'. "
                "Devuelve un objeto con las claves 'alimento' y 'cantidad'.",
            )
        ],
        max_tokens=100,
        json_mode=True,
    )
    response = await provider.complete(request, tier=ModelTier.FAST)
    data = json.loads(response.content)
    assert isinstance(data, dict)
    assert "alimento" in data
    assert response.model_used.startswith(get_settings().ANTHROPIC_MODEL_FAST)
    assert response.stop_reason is StopReason.END_TURN


async def test_ca4_us006_request_con_tools_retorna_tool_calls(
    provider: AnthropicProvider,
) -> None:
    """CA-4 de US-006: contra Claude real, `tools` produce `tool_calls`; y el ciclo cierra."""
    request = CompletionRequest(
        messages=[Message(role="user", content="Acabo de tomarme 3 vasos de agua, anótalos.")],
        system_prompt="Eres Koach. Usa las herramientas disponibles cuando apliquen.",
        max_tokens=300,
        tools=[_TOOL],
    )
    first = await provider.complete(request)

    assert first.stop_reason is StopReason.TOOL_USE
    assert first.tool_calls, "el modelo debió invocar la tool"
    call = first.tool_calls[0]
    assert call.name == "registrar_agua"
    assert call.arguments.get("vasos") == 3

    final = await provider.continue_with_tool_results(
        request,
        first.tool_calls,
        [ToolResult(tool_call_id=call.id, content='{"ok": true, "total_hoy": 3}')],
    )
    assert final.stop_reason is StopReason.END_TURN
    assert final.content.strip()


async def test_analyze_image_real(provider: AnthropicProvider) -> None:
    text = await provider.analyze_image(_png_1x1(), "Describe esta imagen en una frase muy corta.")
    assert text.strip()
