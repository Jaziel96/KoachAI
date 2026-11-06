"""Fakes de los puertos de deduplicación y cola para tests del webhook."""

from __future__ import annotations

from app.ports.dedup import MessageDeduplicator
from app.ports.messaging import IncomingMessage
from app.ports.queue import MessageQueue


class FakeDeduplicator(MessageDeduplicator):
    def __init__(self) -> None:
        self.seen: set[str] = set()

    async def claim(self, message_id: str) -> bool:
        if message_id in self.seen:
            return False
        self.seen.add(message_id)
        return True

    async def release(self, message_id: str) -> None:
        self.seen.discard(message_id)


class FakeQueue(MessageQueue):
    def __init__(self, fail: bool = False) -> None:
        self.messages: list[IncomingMessage] = []
        self.fail = fail

    async def enqueue_incoming(self, message: IncomingMessage) -> None:
        if self.fail:
            raise RuntimeError("cola caída")
        self.messages.append(message)
