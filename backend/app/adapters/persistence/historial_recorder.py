"""Registro de mensajes salientes en `historial_conversacion` (US-017, RF-4).

Limitación conocida (pendiente de validar contra una DB real): `users` tiene RLS
que solo permite SELECT del propio usuario, y aquí se busca el usuario por
teléfono *antes* de conocer su `user_id`. Funciona únicamente si la conexión de
la aplicación evita RLS (p. ej. rol dueño de la tabla). Si no, la búsqueda no
devuelve filas y el mensaje se omite del historial (con warning, sin fallar).
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select

from app.adapters.persistence.db import get_session
from app.adapters.persistence.models import HistorialConversacion, User
from app.core.logging import get_logger
from app.ports.recorder import OutgoingMessageRecorder

logger = get_logger(__name__)


class SqlOutgoingMessageRecorder(OutgoingMessageRecorder):
    async def record(self, to: str, text: str, message_id: str) -> None:
        async with get_session() as session:
            result = await session.execute(select(User.id).where(User.phone.in_([to, f"+{to}"])))
            user_id = result.scalar_one_or_none()

        if user_id is None:
            logger.warning("outgoing_message_unknown_user", message_id=message_id)
            return

        async with get_session(str(user_id)) as session:
            session.add(
                HistorialConversacion(
                    user_id=user_id,
                    fecha=datetime.now(UTC),
                    role="assistant",
                    content=text,
                    canal="whatsapp",
                    message_id_externo=message_id,
                )
            )
