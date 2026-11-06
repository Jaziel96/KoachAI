"""Puerto de registro de mensajes salientes (US-017, RF-4).

Agnóstico de almacenamiento: la implementación (`historial_conversacion` en
Postgres) vive en `app/adapters/persistence/`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class OutgoingMessageRecorder(ABC):
    @abstractmethod
    async def record(self, to: str, text: str, message_id: str) -> None:
        """Registra un mensaje ya enviado, con el id que le asignó el canal."""
        ...
