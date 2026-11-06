"""Tests del registro de mensajes salientes en `historial_conversacion` (US-017, RF-4)."""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from app.adapters.persistence.historial_recorder import SqlOutgoingMessageRecorder
from app.adapters.persistence.models import HistorialConversacion


def _fake_get_session(session: MagicMock, calls: list[str | None]) -> Any:
    @asynccontextmanager
    async def _get_session(user_id: str | None = None) -> AsyncIterator[MagicMock]:
        calls.append(user_id)
        yield session

    return _get_session


def _session(user_id: uuid.UUID | None) -> MagicMock:
    session = MagicMock()
    session.execute = AsyncMock()
    session.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=user_id))
    return session


async def test_registra_el_mensaje_con_el_message_id_de_meta() -> None:
    uid = uuid.uuid4()
    session, calls = _session(uid), []
    with patch(
        "app.adapters.persistence.historial_recorder.get_session",
        _fake_get_session(session, calls),
    ):
        await SqlOutgoingMessageRecorder().record("5215512345678", "Hola", "wamid.1")

    [fila] = [c.args[0] for c in session.add.call_args_list]
    assert isinstance(fila, HistorialConversacion)
    assert fila.user_id == uid
    assert fila.role == "assistant"
    assert fila.canal == "whatsapp"
    assert fila.content == "Hola"
    assert fila.message_id_externo == "wamid.1"
    assert fila.fecha is not None
    # primera sesión (búsqueda del usuario) sin RLS; la escritura, con el contexto del usuario
    assert calls == [None, str(uid)]


async def test_usuario_desconocido_no_escribe_ni_lanza() -> None:
    session, calls = _session(None), []
    with patch(
        "app.adapters.persistence.historial_recorder.get_session",
        _fake_get_session(session, calls),
    ):
        await SqlOutgoingMessageRecorder().record("5215512345678", "Hola", "wamid.1")

    session.add.assert_not_called()
    assert calls == [None]
