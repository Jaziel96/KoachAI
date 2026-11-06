"""Tests del parseo de payloads de Meta a `IncomingMessage` (US-016, CA-5)."""

from typing import Any

from app.adapters.whatsapp.parser import parse_webhook_payload
from app.ports.messaging import MessageType


def _payload(
    *messages: dict[str, Any], statuses: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    value: dict[str, Any] = {"messages": list(messages)}
    if statuses is not None:
        value["statuses"] = statuses
    return {
        "object": "whatsapp_business_account",
        "entry": [{"changes": [{"value": value}]}],
    }


def _base(tipo: str, **extra: Any) -> dict[str, Any]:
    return {
        "from": "5215512345678",
        "id": "wamid.1",
        "timestamp": "1700000000",
        "type": tipo,
        **extra,
    }


def test_texto() -> None:
    [msg] = parse_webhook_payload(_payload(_base("text", text={"body": "hola"})))
    assert msg.channel == "whatsapp"
    assert msg.type is MessageType.TEXT
    assert msg.text == "hola"
    assert msg.from_id == "5215512345678"
    assert msg.message_id == "wamid.1"
    assert msg.timestamp.year == 2023
    assert msg.timestamp.tzinfo is not None


def test_audio() -> None:
    [msg] = parse_webhook_payload(_payload(_base("audio", audio={"id": "media-1"})))
    assert msg.type is MessageType.AUDIO
    assert msg.media_url == "media-1"
    assert msg.text is None


def test_imagen_con_caption() -> None:
    [msg] = parse_webhook_payload(
        _payload(_base("image", image={"id": "media-2", "caption": "mi comida"}))
    )
    assert msg.type is MessageType.IMAGE
    assert msg.media_url == "media-2"
    assert msg.text == "mi comida"


def test_documento() -> None:
    [msg] = parse_webhook_payload(_payload(_base("document", document={"id": "media-3"})))
    assert msg.type is MessageType.DOCUMENT


def test_respuesta_de_boton_interactive() -> None:
    [msg] = parse_webhook_payload(
        _payload(
            _base(
                "interactive",
                interactive={
                    "type": "button_reply",
                    "button_reply": {"id": "ejercicio_completo", "title": "Completa"},
                },
            )
        )
    )
    assert msg.type is MessageType.BUTTON_REPLY
    assert msg.button_payload == "ejercicio_completo"


def test_respuesta_de_boton_de_template() -> None:
    [msg] = parse_webhook_payload(_payload(_base("button", button={"payload": "si", "text": "Sí"})))
    assert msg.type is MessageType.BUTTON_REPLY
    assert msg.button_payload == "si"


def test_varios_mensajes_en_un_payload() -> None:
    segundo = {**_base("text", text={"body": "b"}), "id": "wamid.2"}
    msgs = parse_webhook_payload(_payload(_base("text", text={"body": "a"}), segundo))
    assert [m.message_id for m in msgs] == ["wamid.1", "wamid.2"]


def test_ignora_estatus_y_tipos_no_soportados() -> None:
    assert parse_webhook_payload(_payload(statuses=[{"id": "x", "status": "read"}])) == []
    assert parse_webhook_payload(_payload(_base("sticker", sticker={"id": "s"}))) == []


def test_payload_malformado_no_lanza() -> None:
    for basura in (None, [], "x", {}, {"entry": "x"}, {"entry": [{"changes": [None]}]}):
        assert parse_webhook_payload(basura) == []
    assert parse_webhook_payload(_payload(_base("text", text={}))) == []
    assert parse_webhook_payload(_payload({"type": "text"})) == []
