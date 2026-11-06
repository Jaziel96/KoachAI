"""Canal de WhatsApp Cloud API: envío de texto (US-017).

Implementa `MessagingChannel`. Por ahora solo `send_text`; botones (US-018),
documentos y plantillas (US-019) llegan en sus propias US. No invoca `app/ai/`.

Política de reintentos: se reintentan errores de *conexión* (la petición nunca
salió), 429 y 5xx, con backoff exponencial y jitter. Un timeout de lectura NO se
reintenta: Meta pudo haber entregado el mensaje y no ofrece clave de
idempotencia, así que reintentar podría duplicarlo.
"""

from __future__ import annotations

import asyncio
import random
import re
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

import httpx

from app.adapters.whatsapp.text_splitter import split_text
from app.core.logging import get_logger
from app.ports.messaging import (
    Button,
    MessagingChannel,
    MessagingPermanentError,
    MessagingTransientError,
)
from app.ports.recorder import OutgoingMessageRecorder

if TYPE_CHECKING:
    from app.core.config import Settings

logger = get_logger(__name__)

_PHONE_RE = re.compile(r"^\d{10,15}$")  # E.164: hasta 15 dígitos
_RETRY_AFTER_CAP_SECONDS = 30.0
_BACKOFF_BASE_SECONDS = 0.5
_BACKOFF_CAP_SECONDS = 8.0


def normalize_phone(to: str) -> str:
    """Normaliza a solo dígitos (E.164 sin `+`). El error no incluye el valor recibido."""
    digits = re.sub(r"[\s\-().]", "", to).removeprefix("+")
    if not _PHONE_RE.match(digits):
        raise MessagingPermanentError("Destinatario inválido: se esperaba un teléfono E.164")
    return digits


def _mask(phone: str) -> str:
    return f"***{phone[-4:]}"


class WhatsAppChannel(MessagingChannel):
    def __init__(
        self,
        token: str,
        phone_number_id: str,
        api_version: str,
        *,
        base_url: str = "https://graph.facebook.com",
        client: httpx.AsyncClient | None = None,
        recorder: OutgoingMessageRecorder | None = None,
        max_retries: int = 3,
        timeout: float = 10.0,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self._token = token
        self._url = f"{base_url.rstrip('/')}/{api_version}/{phone_number_id}/messages"
        self._client = client or httpx.AsyncClient()
        self._recorder = recorder
        self._max_retries = max_retries
        self._timeout = timeout
        self._sleep = sleep

    @classmethod
    def from_settings(
        cls, settings: Settings, recorder: OutgoingMessageRecorder | None = None
    ) -> WhatsAppChannel:
        if not settings.WHATSAPP_API_VERSION:
            raise ValueError("WHATSAPP_API_VERSION no está configurada")
        return cls(
            token=settings.WHATSAPP_TOKEN.get_secret_value(),
            phone_number_id=settings.WHATSAPP_PHONE_NUMBER_ID,
            api_version=settings.WHATSAPP_API_VERSION,
            base_url=settings.WHATSAPP_BASE_URL,
            recorder=recorder,
            max_retries=settings.WHATSAPP_MAX_RETRIES,
            timeout=settings.WHATSAPP_TIMEOUT_SECONDS,
        )

    async def send_text(self, to: str, text: str) -> str:
        """Envía texto; si excede 4096 caracteres lo divide y devuelve el id de la 1.ª parte."""
        destino = normalize_phone(to)
        partes = split_text(text)
        if not partes:
            raise MessagingPermanentError("El mensaje está vacío")

        primer_id: str | None = None
        for parte in partes:
            message_id = await self._send_part(destino, parte)
            primer_id = primer_id or message_id
            await self._record(destino, parte, message_id)
        assert primer_id is not None
        return primer_id

    async def send_buttons(self, to: str, text: str, buttons: list[Button]) -> str:
        raise NotImplementedError("send_buttons llega en US-018")

    async def send_document(self, to: str, url: str, caption: str | None) -> str:
        raise NotImplementedError("send_document llega en US-019")

    async def send_template(self, to: str, template_name: str, variables: dict[str, str]) -> str:
        raise NotImplementedError("send_template llega en US-019")

    async def _record(self, to: str, text: str, message_id: str) -> None:
        if self._recorder is None:
            return
        try:
            await self._recorder.record(to, text, message_id)
        except Exception as exc:
            # El mensaje ya se envió: un fallo de auditoría no debe presentarse como fallo de envío.
            logger.error(
                "whatsapp_outgoing_record_failed", message_id=message_id, error=type(exc).__name__
            )

    async def _send_part(self, to: str, body: str) -> str:
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": body},
        }
        headers = {"Authorization": f"Bearer {self._token}"}

        for attempt in range(self._max_retries + 1):
            es_ultimo = attempt == self._max_retries
            try:
                response = await self._client.post(
                    self._url, json=payload, headers=headers, timeout=self._timeout
                )
            except (httpx.ConnectError, httpx.ConnectTimeout, httpx.PoolTimeout) as exc:
                logger.warning(
                    "whatsapp_send_connect_error",
                    to=_mask(to),
                    attempt=attempt,
                    error=type(exc).__name__,
                )
                if es_ultimo:
                    raise MessagingTransientError(
                        "No se pudo conectar con WhatsApp tras varios intentos"
                    ) from exc
                await self._sleep(self._backoff(attempt))
                continue
            except httpx.HTTPError as exc:
                raise MessagingTransientError(
                    "Resultado incierto del envío a WhatsApp (sin respuesta); "
                    "no se reintenta para evitar duplicados"
                ) from exc

            if response.is_success:
                return self._extract_message_id(response)

            status = response.status_code
            if status == 429 or status >= 500:
                logger.warning(
                    "whatsapp_send_retryable", to=_mask(to), status=status, attempt=attempt
                )
                if es_ultimo:
                    raise MessagingTransientError(
                        f"WhatsApp no disponible (HTTP {status}) tras varios intentos"
                    )
                await self._sleep(self._retry_delay(response, attempt))
                continue

            code = self._error_code(response)
            logger.error("whatsapp_send_rejected", to=_mask(to), status=status, code=code)
            raise MessagingPermanentError(
                f"WhatsApp rechazó el envío (HTTP {status}, código {code})"
            )

        raise AssertionError("inalcanzable")  # pragma: no cover

    @staticmethod
    def _extract_message_id(response: httpx.Response) -> str:
        try:
            message_id = response.json()["messages"][0]["id"]
        except (ValueError, KeyError, IndexError, TypeError):
            message_id = None
        if not isinstance(message_id, str) or not message_id:
            # Un 200 sin id: no se reintenta, el mensaje probablemente ya salió.
            raise MessagingPermanentError("Respuesta inesperada de WhatsApp: sin id de mensaje")
        return message_id

    @staticmethod
    def _error_code(response: httpx.Response) -> Any:
        try:
            return response.json()["error"]["code"]
        except (ValueError, KeyError, TypeError):
            return "desconocido"

    @staticmethod
    def _backoff(attempt: int) -> float:
        base = min(_BACKOFF_CAP_SECONDS, _BACKOFF_BASE_SECONDS * float(2**attempt))
        return base * random.uniform(0.5, 1.0)

    def _retry_delay(self, response: httpx.Response, attempt: int) -> float:
        try:
            return min(_RETRY_AFTER_CAP_SECONDS, max(0.0, float(response.headers["Retry-After"])))
        except (KeyError, ValueError):
            return self._backoff(attempt)
