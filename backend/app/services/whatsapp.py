import asyncio
import logging

from app.db.supabase import get_client
from app.messages.es_mx import ERROR_TECNICO, hola_de_nuevo
from app.services.onboarding import handle_onboarding
from app.services.whatsapp_sender import send_message

logger = logging.getLogger(__name__)


async def handle_message(phone_number: str, message_text: str) -> None:
    """Detecta si el usuario es nuevo o existente y enruta apropiadamente."""
    try:
        usuario = await _buscar_usuario(phone_number)
        if usuario:
            await send_message(phone_number, hola_de_nuevo(usuario["nombre"]))
        else:
            await handle_onboarding(phone_number, message_text)
    except Exception as exc:
        logger.error(f"Error crítico en handle_message para {phone_number}: {exc}")
        try:
            await send_message(phone_number, ERROR_TECNICO)
        except Exception as send_exc:
            logger.critical(f"No se pudo enviar mensaje de error a {phone_number}: {send_exc}")


async def _buscar_usuario(phone_number: str) -> dict | None:
    """Busca el usuario en la tabla usuarios por número de teléfono."""
    client = get_client()
    result = await asyncio.to_thread(
        lambda: client.table("usuarios")
            .select("nombre")
            .eq("phone_number", phone_number)
            .execute()
    )
    return result.data[0] if result.data else None
