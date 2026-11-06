"""Tests de `WhatsAppChannel.send_text` (US-017), sin red real (httpx.MockTransport)."""

from __future__ import annotations

import ast
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import httpx
import pytest
from pydantic import SecretStr

from app.adapters.whatsapp.channel import WhatsAppChannel
from app.ports.messaging import (
    Button,
    MessagingChannel,
    MessagingPermanentError,
    MessagingTransientError,
)
from app.ports.recorder import OutgoingMessageRecorder

TOKEN = "secret-token-xyz"
PHONE = "5215512345678"


def _ok(message_id: str = "wamid.OK") -> httpx.Response:
    return httpx.Response(200, json={"messages": [{"id": message_id}]})


class Harness:
    """Entrega respuestas/excepciones en orden; repite la última cuando se agotan."""

    def __init__(self, *responses: httpx.Response | Exception) -> None:
        self.requests: list[httpx.Request] = []
        self.sleeps: list[float] = []
        self._responses = list(responses)

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        item = self._responses.pop(0) if len(self._responses) > 1 else self._responses[0]
        if isinstance(item, Exception):
            raise item
        return item

    async def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)

    def bodies(self) -> list[dict[str, Any]]:
        return [json.loads(r.content) for r in self.requests]


class FakeRecorder(OutgoingMessageRecorder):
    def __init__(self, fail: bool = False) -> None:
        self.calls: list[tuple[str, str, str]] = []
        self.fail = fail

    async def record(self, to: str, text: str, message_id: str) -> None:
        if self.fail:
            raise RuntimeError("db caída")
        self.calls.append((to, text, message_id))


def _channel(
    h: Harness, recorder: OutgoingMessageRecorder | None = None, max_retries: int = 3
) -> WhatsAppChannel:
    return WhatsAppChannel(
        token=TOKEN,
        phone_number_id="123456",
        api_version="v99.0",
        client=httpx.AsyncClient(transport=httpx.MockTransport(h.handler)),
        recorder=recorder,
        max_retries=max_retries,
        sleep=h.sleep,
    )


async def test_envia_texto_y_devuelve_el_message_id_de_meta() -> None:
    h = Harness(_ok("wamid.ABC"))
    message_id = await _channel(h).send_text(PHONE, "Hola")

    assert message_id == "wamid.ABC"
    [request] = h.requests
    assert request.url.path == "/v99.0/123456/messages"
    assert request.headers["authorization"] == f"Bearer {TOKEN}"
    assert h.bodies() == [
        {"messaging_product": "whatsapp", "to": PHONE, "type": "text", "text": {"body": "Hola"}}
    ]


async def test_ca2_error_de_conexion_dispara_reintento() -> None:
    h = Harness(httpx.ConnectError("sin red"), _ok())
    assert await _channel(h).send_text(PHONE, "Hola") == "wamid.OK"
    assert len(h.requests) == 2
    assert len(h.sleeps) == 1


async def test_5xx_se_reintenta_con_backoff() -> None:
    h = Harness(httpx.Response(503), httpx.Response(502), _ok())
    assert await _channel(h).send_text(PHONE, "Hola") == "wamid.OK"
    assert len(h.requests) == 3
    assert all(0 < s <= 8.0 for s in h.sleeps)


async def test_429_respeta_retry_after() -> None:
    h = Harness(httpx.Response(429, headers={"Retry-After": "7"}), _ok())
    await _channel(h).send_text(PHONE, "Hola")
    assert h.sleeps == [7.0]


async def test_retry_after_se_topa() -> None:
    h = Harness(httpx.Response(429, headers={"Retry-After": "9999"}), _ok())
    await _channel(h).send_text(PHONE, "Hola")
    assert h.sleeps == [30.0]


async def test_agotados_los_reintentos_lanza_error_transitorio() -> None:
    h = Harness(httpx.Response(503))
    with pytest.raises(MessagingTransientError):
        await _channel(h, max_retries=2).send_text(PHONE, "Hola")
    assert len(h.requests) == 3


async def test_4xx_es_permanente_no_se_reintenta_y_no_filtra_el_cuerpo() -> None:
    cuerpo = {"error": {"code": 131047, "message": "detalle interno con 5215512345678"}}
    h = Harness(httpx.Response(400, json=cuerpo))

    with pytest.raises(MessagingPermanentError) as info:
        await _channel(h).send_text(PHONE, "Hola")

    assert len(h.requests) == 1
    mensaje = str(info.value)
    assert "131047" in mensaje
    assert "detalle interno" not in mensaje
    assert PHONE not in mensaje
    assert TOKEN not in mensaje


async def test_timeout_de_lectura_no_se_reintenta_para_no_duplicar() -> None:
    h = Harness(httpx.ReadTimeout("sin respuesta"))
    with pytest.raises(MessagingTransientError):
        await _channel(h).send_text(PHONE, "Hola")
    assert len(h.requests) == 1


async def test_200_sin_message_id_es_error_permanente() -> None:
    h = Harness(httpx.Response(200, json={"algo": "raro"}))
    with pytest.raises(MessagingPermanentError):
        await _channel(h).send_text(PHONE, "Hola")
    assert len(h.requests) == 1


async def test_mensaje_largo_se_divide_devuelve_el_primer_id_y_registra_cada_parte() -> None:
    h = Harness(_ok("wamid.1"), _ok("wamid.2"), _ok("wamid.3"))
    recorder = FakeRecorder()
    texto = " ".join(["palabra"] * 1000)  # 7999 caracteres → 2 partes

    message_id = await _channel(h, recorder).send_text(PHONE, texto)

    assert message_id == "wamid.1"
    cuerpos = [b["text"]["body"] for b in h.bodies()]
    assert len(cuerpos) == 2
    assert all(len(c) <= 4096 for c in cuerpos)
    assert [(to, mid) for to, _, mid in recorder.calls] == [(PHONE, "wamid.1"), (PHONE, "wamid.2")]
    assert [t for _, t, _ in recorder.calls] == cuerpos


async def test_si_falla_el_registro_el_envio_no_falla() -> None:
    h = Harness(_ok("wamid.1"))
    assert await _channel(h, FakeRecorder(fail=True)).send_text(PHONE, "Hola") == "wamid.1"


async def test_telefono_se_normaliza_a_digitos() -> None:
    h = Harness(_ok())
    await _channel(h).send_text("+52 1 55-1234-5678", "Hola")
    assert h.bodies()[0]["to"] == PHONE


@pytest.mark.parametrize("invalido", ["", "abc", "123", "+" + "9" * 20, "5215512345678; DROP"])
async def test_destinatario_invalido_se_rechaza_sin_llamar_a_meta(invalido: str) -> None:
    h = Harness(_ok())
    with pytest.raises(MessagingPermanentError) as info:
        await _channel(h).send_text(invalido, "Hola")
    assert h.requests == []
    assert invalido not in str(info.value) or invalido == ""


async def test_texto_vacio_se_rechaza() -> None:
    h = Harness(_ok())
    with pytest.raises(MessagingPermanentError):
        await _channel(h).send_text(PHONE, "   ")
    assert h.requests == []


async def test_metodos_de_otras_us_aun_no_estan_implementados() -> None:
    canal = _channel(Harness(_ok()))
    with pytest.raises(NotImplementedError):
        await canal.send_buttons(PHONE, "x", [Button(id="a", title="A")])
    with pytest.raises(NotImplementedError):
        await canal.send_document(PHONE, "https://x.test/d.pdf", None)
    with pytest.raises(NotImplementedError):
        await canal.send_template(PHONE, "plantilla", {})


def test_implementa_la_interface() -> None:
    assert issubclass(WhatsAppChannel, MessagingChannel)


def test_from_settings_exige_api_version() -> None:
    base: dict[str, Any] = {
        "WHATSAPP_TOKEN": SecretStr(TOKEN),
        "WHATSAPP_PHONE_NUMBER_ID": "123456",
        "WHATSAPP_BASE_URL": "https://graph.facebook.com",
        "WHATSAPP_TIMEOUT_SECONDS": 10.0,
        "WHATSAPP_MAX_RETRIES": 3,
    }
    with pytest.raises(ValueError, match="WHATSAPP_API_VERSION"):
        WhatsAppChannel.from_settings(SimpleNamespace(**base, WHATSAPP_API_VERSION=None))  # type: ignore[arg-type]
    canal = WhatsAppChannel.from_settings(  # type: ignore[arg-type]
        SimpleNamespace(**base, WHATSAPP_API_VERSION="v99.0")
    )
    assert isinstance(canal, WhatsAppChannel)


def test_el_adaptador_no_importa_app_ai() -> None:
    """Excepción de M5: el canal de mensajería no puede invocar IA."""
    fuente = Path(__file__).resolve().parents[3] / "app" / "adapters" / "whatsapp" / "channel.py"
    modulos: set[str] = set()
    for nodo in ast.walk(ast.parse(fuente.read_text(encoding="utf-8"))):
        if isinstance(nodo, ast.Import):
            modulos.update(a.name for a in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            modulos.add(nodo.module)
    assert not any(m == "app.ai" or m.startswith("app.ai.") for m in modulos)
