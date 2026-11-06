"""Interface de mensajería agnóstica de canal (US-015).

Ningún import de aquí debe depender de WhatsApp ni de ningún canal concreto
(CA-2 de US-015). Las implementaciones (`WhatsAppChannel`, chat en app) viven
en `app/adapters/` y la lógica de negocio solo conoce esta interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Literal


class MessagingError(Exception):
    """Error al enviar un mensaje. Los mensajes nunca incluyen el cuerpo de la
    respuesta del canal, ni teléfonos, ni credenciales."""


class MessagingTransientError(MessagingError):
    """Falla temporal (red, indisponibilidad) o de resultado incierto."""


class MessagingPermanentError(MessagingError):
    """El canal rechazó el envío o la petición es inválida; reintentar no ayuda."""


class MessageType(StrEnum):
    """Tipo de contenido de un mensaje entrante (RF-3)."""

    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    BUTTON_REPLY = "button_reply"
    DOCUMENT = "document"


@dataclass(frozen=True, slots=True)
class Button:
    """Botón de respuesta rápida, común a WhatsApp y chat en app."""

    id: str
    title: str


@dataclass(frozen=True, slots=True)
class IncomingMessage:
    """Mensaje entrante normalizado, agnóstico de canal (RF-2).

    Inmutable: un mensaje ya revisado por el screening de crisis no puede
    alterarse después. `from_id`, `text` y `media_url` quedan fuera del `repr`
    para que logs y tracebacks no filtren datos personales.
    """

    channel: Literal["whatsapp", "app"]
    from_id: str = field(repr=False)  # teléfono o user_id
    message_id: str
    type: MessageType
    timestamp: datetime
    text: str | None = field(default=None, repr=False)
    media_url: str | None = field(default=None, repr=False)
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
