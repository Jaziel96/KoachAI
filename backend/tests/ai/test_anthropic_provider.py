"""Tests unitarios de US-007: AnthropicProvider con el SDK mockeado.

Deben pasar siempre, sin red ni API key. La verificación contra la API real
(CA-4 heredado de US-006) vive en `test_anthropic_integration.py`.
"""

from __future__ import annotations

import ast
import json
import logging
from collections.abc import AsyncIterator
from pathlib import Path
from types import TracebackType
from typing import Any

import anthropic
import httpx2
import pytest
from anthropic.types import Message as SdkMessage
from anthropic.types import TextBlock, ToolUseBlock, Usage
from pydantic import SecretStr

from app.ai.exceptions import (
    AIProviderError,
    ContentFilterError,
    InvalidResponseError,
    ProviderUnavailableError,
    RateLimitError,
    UnsupportedTierError,
)
from app.ai.providers.anthropic_provider import AnthropicProvider
from app.ai.providers.base_provider import (
    CompletionRequest,
    LLMProvider,
    Message,
    ModelTier,
    StopReason,
    ToolCall,
    ToolDefinition,
    ToolResult,
    VisionProvider,
)
from app.core.config import ModelPricing

MODEL = "modelo-de-prueba"
FAST_MODEL = "modelo-rapido"
_REQUEST = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
_PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 16


# ------------------------------------------------------------------ fakes


def _sdk_message(
    content: list[TextBlock | ToolUseBlock],
    *,
    stop_reason: str = "end_turn",
    tokens_in: int = 100,
    tokens_out: int = 50,
) -> SdkMessage:
    return SdkMessage(
        id="msg_1",
        type="message",
        role="assistant",
        model=MODEL,
        content=list(content),
        stop_reason=stop_reason,  # type: ignore[arg-type]
        stop_sequence=None,
        usage=Usage(input_tokens=tokens_in, output_tokens=tokens_out),
    )


def _text(text: str, **kwargs: Any) -> SdkMessage:
    return _sdk_message([TextBlock(type="text", text=text, citations=None)], **kwargs)


def _status_error(
    cls: type[anthropic.APIStatusError], status: int, headers: dict[str, str] | None = None
) -> anthropic.APIStatusError:
    response = httpx2.Response(status, request=_REQUEST, headers=headers or {})
    return cls("error", response=response, body=None)


class _FakeStream:
    def __init__(self, chunks: list[str], fail_after: BaseException | None = None) -> None:
        self._chunks = chunks
        self._fail_after = fail_after

    async def __aenter__(self) -> _FakeStream:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        return None

    @property
    def text_stream(self) -> AsyncIterator[str]:
        async def gen() -> AsyncIterator[str]:
            for chunk in self._chunks:
                yield chunk
            if self._fail_after is not None:
                raise self._fail_after

        return gen()


class _FakeMessages:
    def __init__(self, outcomes: list[Any]) -> None:
        self._outcomes = outcomes
        self.calls: list[dict[str, Any]] = []

    async def create(self, **kwargs: Any) -> SdkMessage:
        self.calls.append(kwargs)
        outcome = self._outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        assert isinstance(outcome, SdkMessage)
        return outcome

    def stream(self, **kwargs: Any) -> _FakeStream:
        self.calls.append(kwargs)
        outcome = self._outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        assert isinstance(outcome, _FakeStream)
        return outcome


class _FakeModels:
    def __init__(self, error: BaseException | None = None) -> None:
        self._error = error
        self.retrieved: list[str] = []

    async def retrieve(self, model: str) -> object:
        self.retrieved.append(model)
        if self._error is not None:
            raise self._error
        return object()


class _FakeClient:
    def __init__(self, outcomes: list[Any], models_error: BaseException | None = None) -> None:
        self.messages = _FakeMessages(outcomes)
        self.models = _FakeModels(models_error)


class _Sleeper:
    def __init__(self) -> None:
        self.delays: list[float] = []

    async def __call__(self, seconds: float) -> None:
        self.delays.append(seconds)


def _provider(
    outcomes: list[Any],
    *,
    pricing: dict[str, ModelPricing] | None = None,
    sleeper: _Sleeper | None = None,
    models_error: BaseException | None = None,
    max_retries: int = 3,
) -> tuple[AnthropicProvider, _FakeClient, _Sleeper]:
    client = _FakeClient(outcomes, models_error)
    sleeper = sleeper or _Sleeper()
    provider = AnthropicProvider(
        api_key=SecretStr("sk-ant-test-key"),
        model_map={
            ModelTier.FAST: FAST_MODEL,
            ModelTier.SMART: MODEL,
            ModelTier.VISION: MODEL,
        },
        pricing=pricing,
        client=client,  # type: ignore[arg-type]
        sleep=sleeper,
        max_retries=max_retries,
        retry_after_cap_seconds=30.0,
    )
    return provider, client, sleeper


def _request(**kwargs: Any) -> CompletionRequest:
    return CompletionRequest(messages=[Message(role="user", content="hola")], **kwargs)


_TOOL = ToolDefinition(
    name="registrar_agua",
    description="Registra vasos de agua",
    input_schema={"type": "object", "properties": {"vasos": {"type": "integer"}}},
)


# ------------------------------------------------------- estructura / contrato


def test_implementa_interfaces_y_declara_capacidades() -> None:
    provider, _, _ = _provider([])
    assert isinstance(provider, LLMProvider)
    assert isinstance(provider, VisionProvider)
    assert provider.name == "anthropic"
    assert provider.supports_tools is True
    assert provider.supported_tiers == [ModelTier.FAST, ModelTier.SMART, ModelTier.VISION]


@pytest.mark.parametrize("faltante", [ModelTier.FAST, ModelTier.SMART, ModelTier.VISION])
def test_model_map_incompleto_falla_al_construir(faltante: ModelTier) -> None:
    completo = {ModelTier.FAST: "f", ModelTier.SMART: "s", ModelTier.VISION: "v"}
    del completo[faltante]
    with pytest.raises(ValueError, match=faltante.value):
        AnthropicProvider(api_key=SecretStr("sk-ant-test-key"), model_map=completo)


def test_cliente_real_se_construye_sin_reintentos_del_sdk_y_con_timeout() -> None:
    provider = AnthropicProvider(
        api_key=SecretStr("sk-ant-test-key"),
        model_map={ModelTier.FAST: MODEL, ModelTier.SMART: MODEL, ModelTier.VISION: MODEL},
        timeout=12.5,
    )
    client = provider._client
    assert client.max_retries == 0
    assert client.timeout == 12.5


def test_from_settings_toma_modelos_y_precios_de_la_configuracion() -> None:
    from app.core.config import Settings

    settings = Settings(
        ANTHROPIC_API_KEY=SecretStr("sk-ant-test-key"),
        ANTHROPIC_MODEL_FAST="modelo-fast",
        ANTHROPIC_MODEL_SMART="modelo-smart",
        ANTHROPIC_MODEL_VISION="modelo-vision",
        ANTHROPIC_PRICING={"modelo-smart": ModelPricing(input_per_mtok=1, output_per_mtok=2)},
    )  # type: ignore[call-arg]
    provider = AnthropicProvider.from_settings(settings)
    assert provider._model_map == {
        ModelTier.FAST: "modelo-fast",
        ModelTier.SMART: "modelo-smart",
        ModelTier.VISION: "modelo-vision",
    }
    assert "modelo-smart" in provider._pricing


def test_settings_default_de_haiku_para_fast() -> None:
    from app.core.config import Settings

    assert Settings.model_fields["ANTHROPIC_MODEL_FAST"].default == "claude-haiku-4-5"


def test_settings_no_trae_precios_por_defecto() -> None:
    from app.core.config import Settings

    assert Settings.model_fields["ANTHROPIC_PRICING"].default == {}


# --------------------------------------------------------------------- CA-1


async def test_ca1_complete_retorna_respuesta_valida() -> None:
    provider, client, _ = _provider([_text("Hola, soy Koach")])
    response = await provider.complete(_request(system_prompt="Eres Koach", max_tokens=200))

    assert response.content == "Hola, soy Koach"
    assert response.tokens_input == 100
    assert response.tokens_output == 50
    assert response.provider == "anthropic"
    assert response.model_used == MODEL
    assert response.stop_reason is StopReason.END_TURN
    assert response.tool_calls is None

    sent = client.messages.calls[0]
    assert sent["model"] == MODEL
    assert sent["max_tokens"] == 200
    assert sent["system"] == [{"type": "text", "text": "Eres Koach"}]
    assert sent["messages"] == [{"role": "user", "content": "hola"}]
    # Excepción documentada al contrato: no se envía temperature.
    assert "temperature" not in sent


async def test_mensajes_con_rol_system_se_pliegan_al_system_prompt() -> None:
    provider, client, _ = _provider([_text("ok")])
    request = CompletionRequest(
        messages=[
            Message(role="system", content="Regla extra"),
            Message(role="user", content="hola"),
        ],
        system_prompt="Base",
    )
    await provider.complete(request)
    sent = client.messages.calls[0]
    assert sent["system"][0]["text"] == "Base\n\nRegla extra"
    assert sent["messages"] == [{"role": "user", "content": "hola"}]


async def test_stop_sequences_se_envian() -> None:
    provider, client, _ = _provider([_text("ok")])
    await provider.complete(_request(stop_sequences=["FIN"]))
    assert client.messages.calls[0]["stop_sequences"] == ["FIN"]


async def test_max_tokens_se_mapea_a_stop_reason() -> None:
    provider, _, _ = _provider([_text("cortado", stop_reason="max_tokens")])
    response = await provider.complete(_request())
    assert response.stop_reason is StopReason.MAX_TOKENS


async def test_refusal_lanza_content_filter_error() -> None:
    provider, _, _ = _provider([_text("", stop_reason="refusal")])
    with pytest.raises(ContentFilterError):
        await provider.complete(_request())


async def test_tier_no_soportado_lanza_unsupported_tier_error() -> None:
    provider, client, _ = _provider([])
    with pytest.raises(UnsupportedTierError):
        await provider.complete(_request(), tier=ModelTier.AUDIO)
    assert client.messages.calls == []


# ------------------------------------------------------------------- tier FAST


async def test_tier_fast_usa_el_modelo_fast_y_smart_el_suyo() -> None:
    provider, client, _ = _provider([_text("rápido"), _text("listo")])
    fast = await provider.complete(_request(), tier=ModelTier.FAST)
    smart = await provider.complete(_request(), tier=ModelTier.SMART)

    assert fast.content == "rápido"
    assert client.messages.calls[0]["model"] == FAST_MODEL
    assert client.messages.calls[1]["model"] == MODEL
    assert smart.content == "listo"


async def test_tier_fast_json_mode_valido_pasa() -> None:
    provider, client, _ = _provider([_text('{"alimento": "tortilla", "kcal": 60}')])
    response = await provider.complete(_request(json_mode=True), tier=ModelTier.FAST)
    assert json.loads(response.content)["alimento"] == "tortilla"
    assert client.messages.calls[0]["model"] == FAST_MODEL
    assert "JSON válido" in client.messages.calls[0]["system"][0]["text"]


async def test_tier_fast_json_mode_invalido_lanza_invalid_response_error() -> None:
    provider, _, _ = _provider([_text("tortilla, 60 kcal")])
    with pytest.raises(InvalidResponseError):
        await provider.complete(_request(json_mode=True), tier=ModelTier.FAST)


async def test_tier_fast_costo_usa_el_precio_de_su_modelo() -> None:
    pricing = {
        FAST_MODEL: ModelPricing(input_per_mtok=1.0, output_per_mtok=5.0),
        MODEL: ModelPricing(input_per_mtok=100.0, output_per_mtok=100.0),
    }
    provider, _, _ = _provider(
        [_text("ok", tokens_in=1_000_000, tokens_out=1_000_000)], pricing=pricing
    )
    response = await provider.complete(_request(), tier=ModelTier.FAST)
    assert response.cost_usd == pytest.approx(6.0)


async def test_tier_fast_sin_precio_configurado_deja_cost_usd_en_none() -> None:
    provider, _, _ = _provider(
        [_text("ok")], pricing={MODEL: ModelPricing(input_per_mtok=1, output_per_mtok=1)}
    )
    response = await provider.complete(_request(), tier=ModelTier.FAST)
    assert response.cost_usd is None


async def test_tier_fast_stream_usa_el_modelo_fast() -> None:
    provider, client, _ = _provider([_FakeStream(["a", "b"])])
    assert [c async for c in provider.stream(_request(), tier=ModelTier.FAST)] == ["a", "b"]
    assert client.messages.calls[0]["model"] == FAST_MODEL


# ------------------------------------------------------- CA-4 de US-006 (tools)


async def test_request_con_tools_retorna_tool_calls() -> None:
    tool_block = ToolUseBlock(
        type="tool_use", id="toolu_1", name="registrar_agua", input={"vasos": 2}
    )
    provider, client, _ = _provider([_sdk_message([tool_block], stop_reason="tool_use")])

    response = await provider.complete(_request(tools=[_TOOL]))

    assert response.stop_reason is StopReason.TOOL_USE
    assert response.tool_calls == [
        ToolCall(id="toolu_1", name="registrar_agua", arguments={"vasos": 2})
    ]
    assert client.messages.calls[0]["tools"] == [
        {
            "name": "registrar_agua",
            "description": "Registra vasos de agua",
            "input_schema": _TOOL.input_schema,
        }
    ]


async def test_continue_with_tool_results_reenvia_el_turno_de_tools() -> None:
    provider, client, _ = _provider([_text("Listo, registré 2 vasos")])
    calls = [ToolCall(id="toolu_1", name="registrar_agua", arguments={"vasos": 2})]
    results = [ToolResult(tool_call_id="toolu_1", content='{"ok": true}')]

    response = await provider.continue_with_tool_results(_request(tools=[_TOOL]), calls, results)

    assert response.content == "Listo, registré 2 vasos"
    sent = client.messages.calls[0]
    assert sent["tools"][0]["name"] == "registrar_agua"
    assert sent["messages"][1:] == [
        {
            "role": "assistant",
            "content": [
                {
                    "type": "tool_use",
                    "id": "toolu_1",
                    "name": "registrar_agua",
                    "input": {"vasos": 2},
                }
            ],
        },
        {
            "role": "user",
            "content": [
                {"type": "tool_result", "tool_use_id": "toolu_1", "content": '{"ok": true}'}
            ],
        },
    ]


async def test_continue_propaga_is_error_y_agrupa_resultados_en_un_solo_turno() -> None:
    provider, client, _ = _provider([_text("No pude")])
    calls = [
        ToolCall(id="a", name="registrar_agua", arguments={}),
        ToolCall(id="b", name="registrar_agua", arguments={}),
    ]
    results = [
        ToolResult(tool_call_id="a", content="ok"),
        ToolResult(tool_call_id="b", content="falló", is_error=True),
    ]
    await provider.continue_with_tool_results(_request(tools=[_TOOL]), calls, results)

    user_turn = client.messages.calls[0]["messages"][-1]
    assert user_turn["role"] == "user"
    assert len(user_turn["content"]) == 2
    assert "is_error" not in user_turn["content"][0]
    assert user_turn["content"][1]["is_error"] is True


async def test_continue_rechaza_resultados_que_no_corresponden_a_los_calls() -> None:
    provider, client, _ = _provider([])
    calls = [ToolCall(id="a", name="registrar_agua", arguments={})]
    with pytest.raises(ValueError, match="ToolResult"):
        await provider.continue_with_tool_results(
            _request(tools=[_TOOL]), calls, [ToolResult(tool_call_id="otro", content="x")]
        )
    assert client.messages.calls == []


# --------------------------------------------------------------------- json_mode


async def test_json_mode_valido_pasa_y_refuerza_el_system_prompt() -> None:
    provider, client, _ = _provider([_text('{"kcal": 350}')])
    response = await provider.complete(_request(json_mode=True, system_prompt="Base"))
    assert json.loads(response.content) == {"kcal": 350}
    assert "JSON válido" in client.messages.calls[0]["system"][0]["text"]


async def test_json_mode_invalido_lanza_invalid_response_error() -> None:
    provider, _, _ = _provider([_text("Claro, aquí tienes: {kcal: 350}")])
    with pytest.raises(InvalidResponseError):
        await provider.complete(_request(json_mode=True))


_KCAL = '{"kcal": 350}'


@pytest.mark.parametrize("tier", [ModelTier.FAST, ModelTier.SMART])
@pytest.mark.parametrize(
    "raw",
    [
        '```json\n{"kcal": 350}\n```',
        '```\n{"kcal": 350}\n```',
        '  \n```json\n{"kcal": 350}\n```\n  ',
        '```json\n{"kcal": 350}```',
        '{"kcal": 350}',
    ],
    ids=["fence-json", "fence-sin-etiqueta", "con-espacios", "cierre-misma-linea", "sin-fence"],
)
async def test_json_mode_quita_un_unico_fence_exterior(raw: str, tier: ModelTier) -> None:
    provider, _, _ = _provider([_text(raw)])
    response = await provider.complete(_request(json_mode=True), tier=tier)
    assert response.content == _KCAL


async def test_json_mode_fence_multilinea_conserva_el_json() -> None:
    provider, _, _ = _provider([_text('```json\n{\n  "a": 1,\n  "b": [1, 2]\n}\n```')])
    response = await provider.complete(_request(json_mode=True))
    assert json.loads(response.content) == {"a": 1, "b": [1, 2]}


@pytest.mark.parametrize(
    "raw",
    [
        "```json\n{kcal: 350}\n```",  # fence + JSON inválido
        'Aquí tienes:\n```json\n{"kcal": 350}\n```',  # prosa antes
        '```json\n{"kcal": 350}\n```\nEspero que sirva.',  # prosa después
        '```json\n{"kcal": 350}',  # fence sin cerrar
        '```{"kcal": 350}```',  # sin salto de línea tras la apertura
        '```json\n{"a": 1}\n```\n\n```json\n{"b": 2}\n```',  # dos fences
        "```json\n```",  # fence vacío
    ],
    ids=[
        "fence-json-invalido",
        "prosa-antes",
        "prosa-despues",
        "sin-cerrar",
        "sin-salto-de-linea",
        "dos-fences",
        "fence-vacio",
    ],
)
async def test_json_mode_rechaza_fences_mal_formados_o_con_prosa(raw: str) -> None:
    provider, _, _ = _provider([_text(raw)])
    with pytest.raises(InvalidResponseError):
        await provider.complete(_request(json_mode=True))


async def test_fuera_de_json_mode_el_fence_no_se_toca() -> None:
    raw = '```json\n{"kcal": 350}\n```'
    provider, _, _ = _provider([_text(raw)])
    response = await provider.complete(_request())
    assert response.content == raw


# --------------------------------------------------------------------- CA-2


async def test_ca2_stream_emite_chunks_progresivamente() -> None:
    provider, _, _ = _provider([_FakeStream(["Ho", "la ", "Koach"])])
    chunks = [c async for c in provider.stream(_request())]
    assert chunks == ["Ho", "la ", "Koach"]


async def test_stream_reintenta_429_antes_del_primer_chunk() -> None:
    provider, client, sleeper = _provider(
        [_status_error(anthropic.RateLimitError, 429), _FakeStream(["ok"])]
    )
    assert [c async for c in provider.stream(_request())] == ["ok"]
    assert len(client.messages.calls) == 2
    assert len(sleeper.delays) == 1


async def test_stream_no_reintenta_despues_de_emitir_texto() -> None:
    boom = _status_error(anthropic.RateLimitError, 429)
    provider, client, sleeper = _provider([_FakeStream(["parcial"], fail_after=boom)])
    received: list[str] = []
    with pytest.raises(RateLimitError):
        async for chunk in provider.stream(_request()):
            received.append(chunk)
    assert received == ["parcial"]
    assert len(client.messages.calls) == 1
    assert sleeper.delays == []


# --------------------------------------------------------------------- CA-3


async def test_ca3_rate_limit_reintenta_con_backoff_y_se_recupera() -> None:
    provider, client, sleeper = _provider(
        [
            _status_error(anthropic.RateLimitError, 429),
            _status_error(anthropic.RateLimitError, 429),
            _text("ok"),
        ]
    )
    response = await provider.complete(_request())
    assert response.content == "ok"
    assert len(client.messages.calls) == 3
    assert len(sleeper.delays) == 2
    # Backoff exponencial con jitter [0.5, 1.0]: 1s base -> 2s base.
    assert 0.5 <= sleeper.delays[0] <= 1.0
    assert 1.0 <= sleeper.delays[1] <= 2.0


async def test_rate_limit_respeta_retry_after_del_servidor() -> None:
    err = _status_error(anthropic.RateLimitError, 429, {"retry-after": "7"})
    provider, _, sleeper = _provider([err, _text("ok")])
    await provider.complete(_request())
    assert sleeper.delays == [7.0]


async def test_retry_after_tiene_tope() -> None:
    err = _status_error(anthropic.RateLimitError, 429, {"retry-after": "3600"})
    provider, _, sleeper = _provider([err, _text("ok")])
    await provider.complete(_request())
    assert sleeper.delays == [30.0]


async def test_rate_limit_agotado_lanza_rate_limit_error() -> None:
    outcomes = [_status_error(anthropic.RateLimitError, 429) for _ in range(4)]
    provider, client, sleeper = _provider(outcomes, max_retries=3)
    with pytest.raises(RateLimitError):
        await provider.complete(_request())
    assert len(client.messages.calls) == 4  # 1 intento + 3 reintentos
    assert len(sleeper.delays) == 3


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (_status_error(anthropic.InternalServerError, 500), ProviderUnavailableError),
        (_status_error(anthropic.AuthenticationError, 401), ProviderUnavailableError),
        (_status_error(anthropic.PermissionDeniedError, 403), ProviderUnavailableError),
        (anthropic.APITimeoutError(request=_REQUEST), ProviderUnavailableError),
        (anthropic.APIConnectionError(request=_REQUEST), ProviderUnavailableError),
        (_status_error(anthropic.BadRequestError, 400), AIProviderError),
    ],
)
async def test_otros_errores_no_se_reintentan_y_se_mapean(
    error: anthropic.APIError, expected: type[AIProviderError]
) -> None:
    provider, client, sleeper = _provider([error, _text("no debería llegar")])
    with pytest.raises(expected) as exc_info:
        await provider.complete(_request())
    assert type(exc_info.value) is expected
    assert len(client.messages.calls) == 1
    assert sleeper.delays == []


# --------------------------------------------------------------------- CA-4


async def test_ca4_health_check_true_con_key_valida() -> None:
    provider, client, _ = _provider([])
    assert await provider.health_check() is True
    assert client.models.retrieved == [MODEL]


async def test_ca4_health_check_false_con_key_invalida() -> None:
    provider, _, _ = _provider([], models_error=_status_error(anthropic.AuthenticationError, 401))
    assert await provider.health_check() is False


async def test_health_check_false_si_no_hay_red() -> None:
    provider, _, _ = _provider([], models_error=anthropic.APIConnectionError(request=_REQUEST))
    assert await provider.health_check() is False


# --------------------------------------------------------------------- CA-5


async def test_ca5_costo_se_calcula_con_la_tabla_de_precios_configurada() -> None:
    pricing = {MODEL: ModelPricing(input_per_mtok=2.0, output_per_mtok=10.0)}
    provider, _, _ = _provider(
        [_text("ok", tokens_in=1_000_000, tokens_out=500_000)], pricing=pricing
    )
    response = await provider.complete(_request())
    # 1M * $2 + 0.5M * $10 = $7
    assert response.cost_usd == pytest.approx(7.0)


async def test_modelo_sin_precio_deja_cost_usd_en_none() -> None:
    provider, _, _ = _provider([_text("ok")], pricing={})
    response = await provider.complete(_request())
    assert response.cost_usd is None


# ----------------------------------------------------------------------- visión


async def test_analyze_image_envia_imagen_base64_con_media_type_detectado() -> None:
    provider, client, _ = _provider([_text("Un plato de frijoles")])
    text = await provider.analyze_image(_PNG, "¿Qué hay en la foto?")
    assert text == "Un plato de frijoles"

    content = client.messages.calls[0]["messages"][0]["content"]
    assert content[0]["type"] == "image"
    assert content[0]["source"]["media_type"] == "image/png"
    assert content[1] == {"type": "text", "text": "¿Qué hay en la foto?"}


async def test_analyze_image_rechaza_formato_desconocido() -> None:
    provider, client, _ = _provider([])
    with pytest.raises(ValueError, match="Formato de imagen"):
        await provider.analyze_image(b"no-es-una-imagen", "x")
    assert client.messages.calls == []


# ----------------------------------------------------------- seguridad / aislamiento


async def test_api_key_y_contenido_de_usuario_no_se_loguean(
    caplog: pytest.LogCaptureFixture,
) -> None:
    from app.core.logging import configure_logging

    configure_logging(json_logs=True)
    provider, _, _ = _provider(
        [_status_error(anthropic.RateLimitError, 429), _text("respuesta privada")]
    )
    request = CompletionRequest(messages=[Message(role="user", content="mi peso es 93 kg")])
    with caplog.at_level(logging.INFO):
        await provider.complete(request)

    logs = caplog.text
    assert "sk-ant-test-key" not in logs
    assert "mi peso es 93 kg" not in logs
    assert "respuesta privada" not in logs
    assert "anthropic_request" in logs


def test_api_key_no_aparece_en_el_repr_del_provider() -> None:
    provider, _, _ = _provider([])
    assert "sk-ant-test-key" not in repr(provider)
    assert "sk-ant-test-key" not in repr(SecretStr("sk-ant-test-key"))


def test_solo_anthropic_provider_importa_el_sdk_anthropic() -> None:
    """Regla no negociable #1: el SDK `anthropic` solo se importa aquí."""
    app_dir = Path(__file__).resolve().parents[2] / "app"
    offenders: list[str] = []
    for path in app_dir.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            if any(n == "anthropic" or n.startswith("anthropic.") for n in names):
                offenders.append(path.name)
    assert set(offenders) == {"anthropic_provider.py"}
