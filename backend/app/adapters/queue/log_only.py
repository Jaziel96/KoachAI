"""Cola provisional: solo registra el mensaje recibido (US-016, RNF-2).

Placeholder hasta que exista el worker de Celery (integración posterior).
No invoca `app/ai/` y no registra teléfono ni texto, solo ids y tipo.
"""

from __future__ import annotations

from app.core.logging import get_logger
from app.ports.messaging import IncomingMessage
from app.ports.queue import MessageQueue

logger = get_logger(__name__)


class LogOnlyMessageQueue(MessageQueue):
    async def enqueue_incoming(self, message: IncomingMessage) -> None:
        logger.info(
            "whatsapp_message_enqueued",
            message_id=message.message_id,
            type=message.type.value,
            channel=message.channel,
        )
