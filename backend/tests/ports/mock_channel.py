"""Canal ficticio mínimo para CA-1/CA-3: implementa la interface completa."""

from __future__ import annotations

from app.ports.messaging import Button, MessagingChannel


class MockMessagingChannel(MessagingChannel):
    """Implementación mínima que registra cada envío en `sent`."""

    def __init__(self) -> None:
        self.sent: list[tuple[str, str, dict[str, object]]] = []

    def _record(self, kind: str, to: str, **payload: object) -> str:
        self.sent.append((kind, to, payload))
        return f"mock-msg-{len(self.sent)}"

    async def send_text(self, to: str, text: str) -> str:
        return self._record("text", to, text=text)

    async def send_buttons(self, to: str, text: str, buttons: list[Button]) -> str:
        return self._record("buttons", to, text=text, buttons=buttons)

    async def send_document(self, to: str, url: str, caption: str | None) -> str:
        return self._record("document", to, url=url, caption=caption)

    async def send_template(self, to: str, template_name: str, variables: dict[str, str]) -> str:
        return self._record("template", to, template_name=template_name, variables=variables)
