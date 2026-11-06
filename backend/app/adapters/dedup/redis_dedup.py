"""Deduplicador de mensajes en Redis (US-016, RF-5): `SET NX` con TTL de 24 h."""

from __future__ import annotations

from typing import Any

from app.ports.dedup import MessageDeduplicator

_TTL_SECONDS = 24 * 60 * 60


class RedisMessageDeduplicator(MessageDeduplicator):
    def __init__(self, client: Any) -> None:  # redis.asyncio.Redis
        self._client = client

    @staticmethod
    def _key(message_id: str) -> str:
        return f"wa:msg:{message_id}"

    async def claim(self, message_id: str) -> bool:
        reclamado = await self._client.set(self._key(message_id), "1", nx=True, ex=_TTL_SECONDS)
        return bool(reclamado)

    async def release(self, message_id: str) -> None:
        await self._client.delete(self._key(message_id))
