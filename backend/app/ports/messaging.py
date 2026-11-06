"""Interface de mensajería agnóstica de canal (US-015).

Ningún import de aquí debe depender de WhatsApp ni de ningún canal concreto
(CA-2 de US-015). Las implementaciones (`WhatsAppChannel`, chat en app) viven
en `app/adapters/` y la lógica de negocio solo conoce esta interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Literal


class MessageType(StrEnum):
    """Tipo de contenido de un mensaje entrante (RF-3)."""

    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    BUTTON_REPLY = "button_reply"
    DOCUMENT = "document"


@dataclass
class Button:
    """Botón de respuesta rápida, común a WhatsApp y chat en app."""

    id: str
    title: str


@dataclass
class IncomingMessage:
    """Mensaje entrante normalizado, agnóstico de canal (RF-2)."""

    channel: Literal["whatsapp", "app"]
    from_id: str  # teléfono o user_id
    message_id: str
    type: MessageType
    timestamp: datetime
    text: str | None = None
    media_url: str | None = None
    button_payload: str | None = None


class MessagingChannel(ABC):
    """Interface que TODOS los canales de mensajería deben implementar (RF-1).

    Cada método retorna el id del mensaje enviado, asignado por el canal.
    """

    @abstractmethod
    async def send_text(self, to: str, text: str) -> str:
        """Envía un mensaje de texto."""
        ...

    @abstractmethod
    async def send_buttons(self, to: str, text: str, buttons: list[Button]) -> str:
        """Envía un mensaje con botones de respuesta rápida."""
        ...

    @abstractmethod
    async def send_document(self, to: str, url: str, caption: str | None) -> str:
        """Envía un documento disponible en `url`."""
        ...

    @abstractmethod
    async def send_template(self, to: str, template_name: str, variables: dict[str, str]) -> str:
        """Envía una plantilla preaprobada con sus variables."""
        ...
