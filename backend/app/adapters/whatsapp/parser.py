"""Parseo de payloads de webhook de Meta a `IncomingMessage` (US-016, RF-4).

Función pura y tolerante: un payload malformado o de un tipo no soportado se
ignora, nunca lanza (Meta reintenta si el webhook no responde 200).

Para audio, imagen y documento, Meta entrega un *media id*, no una URL: se
guarda en `IncomingMessage.media_url` y se resuelve contra la Graph API al
descargar el archivo (entrada no confiable, validar al descargar).
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

from app.ports.messaging import IncomingMessage, MessageType

_MEDIA_TYPES = {
    "audio": MessageType.AUDIO,
    "image": MessageType.IMAGE,
    "document": MessageType.DOCUMENT,
}


def _dict(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _str(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _iter_values(payload: object) -> Iterator[dict[str, Any]]:
    entries = _dict(payload).get("entry")
    for entry in entries if isinstance(entries, list) else []:
        changes = _dict(entry).get("changes")
        for change in changes if isinstance(changes, list) else []:
            yield _dict(_dict(change).get("value"))


def _timestamp(raw: object) -> datetime:
    try:
        return datetime.fromtimestamp(int(str(raw)), tz=UTC)
    except (ValueError, OverflowError, OSError):
        return datetime.now(UTC)


def _parse_message(raw: object) -> IncomingMessage | None:
    data = _dict(raw)
    from_id, message_id, kind = _str(data.get("from")), _str(data.get("id")), _str(data.get("type"))
    if not (from_id and message_id and kind):
        return None

    msg_type: MessageType
    text: str | None = None
    media_id: str | None = None
    button_payload: str | None = None

    if kind == "text":
        msg_type, text = MessageType.TEXT, _str(_dict(data.get("text")).get("body"))
        if text is None:
            return None
    elif kind in _MEDIA_TYPES:
        media = _dict(data.get(kind))
        msg_type, media_id, text = (
            _MEDIA_TYPES[kind],
            _str(media.get("id")),
            _str(media.get("caption")),
        )
        if media_id is None:
            return None
    elif kind == "interactive":
        interactive = _dict(data.get("interactive"))
        if interactive.get("type") != "button_reply":
            return None
        reply = _dict(interactive.get("button_reply"))
        msg_type, button_payload, text = (
            MessageType.BUTTON_REPLY,
            _str(reply.get("id")),
            _str(reply.get("title")),
        )
        if button_payload is None:
            return None
    elif kind == "button":
        button = _dict(data.get("button"))
        msg_type, button_payload, text = (
            MessageType.BUTTON_REPLY,
            _str(button.get("payload")),
            _str(button.get("text")),
        )
        if button_payload is None:
            return None
    else:
        return None

    return IncomingMessage(
        channel="whatsapp",
        from_id=from_id,
        message_id=message_id,
        type=msg_type,
        timestamp=_timestamp(data.get("timestamp")),
        text=text,
        media_url=media_id,
        button_payload=button_payload,
    )


def parse_webhook_payload(payload: object) -> list[IncomingMessage]:
    """Extrae los mensajes entrantes de un payload de Meta; ignora `statuses`."""
    messages: list[IncomingMessage] = []
    for value in _iter_values(payload):
        raw_messages = value.get("messages")
        for raw in raw_messages if isinstance(raw_messages, list) else []:
            parsed = _parse_message(raw)
            if parsed is not None:
                messages.append(parsed)
    return messages
