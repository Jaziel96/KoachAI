import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_GRAPH_API_URL = "https://graph.facebook.com/v18.0/{phone_number_id}/messages"


async def send_message(to: str, text: str) -> None:
    """Envía un mensaje de texto al usuario via WhatsApp Cloud API."""
    url = _GRAPH_API_URL.format(phone_number_id=settings.whatsapp_phone_number_id)
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_token}",
        "Content-Type": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            logger.info(f"Mensaje enviado a {to}")
    except httpx.HTTPStatusError as exc:
        logger.error(
            f"Error HTTP al enviar mensaje a {to}: "
            f"{exc.response.status_code} — {exc.response.text[:200]}"
        )
    except httpx.RequestError as exc:
        logger.error(f"Error de red al enviar mensaje a {to}: {exc}")
