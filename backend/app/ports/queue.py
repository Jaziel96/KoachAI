"""Puerto de cola de procesamiento de mensajes entrantes (US-016, RNF-2).

El webhook solo encola y responde 200; el procesamiento ocurre en un worker.
La implementación real (Celery) llega cuando exista un worker con trabajo útil.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.ports.messaging import IncomingMessage


class MessageQueue(ABC):
    @abstractmethod
    async def enqueue_incoming(self, message: IncomingMessage) -> None:
        """Encola un mensaje entrante para procesamiento asíncrono."""
        ...
