import logging
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from app.core.config import settings
from app.schemas.whatsapp import WhatsAppPayload
from app.services.whatsapp import handle_message

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/webhook", response_class=PlainTextResponse)
async def verify_webhook(
    hub_mode: str | None = Query(default=None, alias="hub.mode"),
    hub_verify_token: str | None = Query(default=None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(default=None, alias="hub.challenge"),
) -> str:
    """Verifica la conexión inicial con Meta (challenge-response)."""
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_verify_token:
        logger.info("Webhook verificado exitosamente por Meta")
        return hub_challenge or ""
    logger.warning(f"Verificación de webhook fallida — mode={hub_mode}, token recibido no coincide")
    raise HTTPException(status_code=403, detail="Verificación fallida")


@router.post("/webhook", status_code=200)
async def receive_message(request: Request, background_tasks: BackgroundTasks) -> dict:
    """Recibe mensajes entrantes de WhatsApp y retorna 200 inmediatamente."""
    try:
        body = await request.json()
        payload = WhatsAppPayload.model_validate(body)

        for entry in payload.entry:
            for change in entry.changes:
                messages = change.value.messages
                if not messages:
                    continue
                for msg in messages:
                    if msg.type != "text":
                        logger.info(f"Mensaje recibido de tipo no-texto: {msg.type} — omitido (msg_id={msg.id})")
                        continue
                    phone_number = msg.from_
                    message_text = msg.text.body if msg.text else ""
                    logger.info(f"Mensaje recibido — phone={phone_number}, msg_id={msg.id}, texto='{message_text}'")
                    background_tasks.add_task(handle_message, phone_number, message_text)

    except Exception as exc:
        logger.warning(f"Payload inesperado o malformado — error={exc}, raw={await _safe_body(request)}")

    return {"status": "ok"}


async def _safe_body(request: Request) -> str:
    try:
        body = await request.body()
        return body.decode("utf-8", errors="replace")[:500]
    except Exception:
        return "<no se pudo leer el body>"
