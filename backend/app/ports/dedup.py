"""Puerto de deduplicación de mensajes entrantes (US-016, RF-5).

Agnóstico de la tecnología de almacenamiento: la implementación (Redis) vive
en `app/adapters/dedup/`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class MessageDeduplicator(ABC):
    """Garantiza que un `message_id` se procese una sola vez."""

    @abstractmethod
    async def claim(self, message_id: str) -> bool:
        """Reclama el mensaje. `True` si es la primera vez; `False` si ya se vio."""
        ...

    @abstractmethod
    async def release(self, message_id: str) -> None:
        """Libera el reclamo, para que un reintento del canal pueda procesarlo.

        Se usa cuando falla el encolado después de `claim()`: sin esto, el
        reintento de Meta se descartaría como duplicado y el mensaje se perdería.
        """
        ...
