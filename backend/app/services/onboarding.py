import asyncio
import logging
import re
from datetime import datetime, timezone

from app.db.supabase import get_client
from app.messages.es_mx import (
    BIENVENIDA_Y_CONSENTIMIENTO,
    CONSENTIMIENTO_RECHAZADO,
    DEMASIADOS_INTENTOS,
    ERROR_EDAD_MINIMA,
    PREGUNTAS,
    RESPUESTA_INVALIDA,
    confirmacion_peso,
    onboarding_completo,
)
from app.services.whatsapp_sender import send_message

logger = logging.getLogger(__name__)

_MAX_INTENTOS = 3

_CONSENT_YES = {"si", "sí", "acepto", "ok", "yes", "claro", "dale", "si acepto", "sí acepto"}
_CONSENT_NO = {"no", "no gracias", "nope", "nel"}

_METAS = {
    "bajar de peso": "bajar de peso",
    "ganar musculo": "ganar músculo",
    "ganar músculo": "ganar músculo",
    "comer mejor": "comer mejor",
    "mas energia": "más energía",
    "más energía": "más energía",
}

_GENEROS = {"hombre", "mujer", "prefiero no decir"}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def handle_onboarding(phone_number: str, message_text: str) -> None:
    """Gestiona el flujo completo de onboarding para un usuario nuevo."""
    text = _normalize(message_text)

    if text == "reiniciar":
        await _delete_state(phone_number)
        await _create_state(phone_number)
        await send_message(phone_number, BIENVENIDA_Y_CONSENTIMIENTO)
        return

    state = await _load_state(phone_number)

    if state is None:
        await _create_state(phone_number)
        await send_message(phone_number, BIENVENIDA_Y_CONSENTIMIENTO)
        return

    paso: int = state["paso_actual"]
    datos: dict = dict(state["datos_parciales"] or {})
    intentos: int = state["intentos_paso"]

    if paso == 0:
        await _handle_consent(phone_number, text, datos, intentos)
    else:
        await _handle_step(phone_number, text, paso, datos, intentos)


# ---------------------------------------------------------------------------
# Step handlers
# ---------------------------------------------------------------------------


async def _handle_consent(
    phone_number: str, text: str, datos: dict, intentos: int
) -> None:
    if text in _CONSENT_YES:
        datos["consintio"] = True
        await _save_state(phone_number, 1, datos, 0)
        await send_message(phone_number, PREGUNTAS[1])
    elif text in _CONSENT_NO:
        await _delete_state(phone_number)
        await send_message(phone_number, CONSENTIMIENTO_RECHAZADO)
    else:
        await _handle_invalid(phone_number, 0, datos, intentos, BIENVENIDA_Y_CONSENTIMIENTO)


async def _handle_step(
    phone_number: str, text: str, paso: int, datos: dict, intentos: int
) -> None:
    if "peso_pendiente_confirmacion" in datos:
        await _handle_weight_confirm(phone_number, text, paso, datos)
        return

    is_valid, value, error = _validate_answer(paso, text)

    if not is_valid:
        if error == "edad_minima":
            await _delete_state(phone_number)
            await send_message(phone_number, ERROR_EDAD_MINIMA)
            return
        if error == "peso_fuera_de_rango":
            datos["peso_pendiente_confirmacion"] = value
            await _save_state(phone_number, paso, datos, 0)
            await send_message(phone_number, confirmacion_peso(value))
            return
        await _handle_invalid(phone_number, paso, datos, intentos, RESPUESTA_INVALIDA[paso])
        return

    datos = _save_answer(paso, value, datos)
    if paso == 7:
        await _complete_onboarding(phone_number, datos)
    else:
        await _save_state(phone_number, paso + 1, datos, 0)
        await send_message(phone_number, PREGUNTAS[paso + 1])


async def _handle_weight_confirm(
    phone_number: str, text: str, paso: int, datos: dict
) -> None:
    peso = datos.pop("peso_pendiente_confirmacion")
    if text in _CONSENT_YES:
        datos = _save_answer(paso, peso, datos)
        await _save_state(phone_number, paso + 1, datos, 0)
        await send_message(phone_number, PREGUNTAS[paso + 1])
    else:
        await _save_state(phone_number, paso, datos, 0)
        await send_message(phone_number, PREGUNTAS[paso])


async def _handle_invalid(
    phone_number: str, paso: int, datos: dict, intentos: int, error_msg: str
) -> None:
    nuevos_intentos = intentos + 1
    await _save_state(phone_number, paso, datos, nuevos_intentos)
    if nuevos_intentos >= _MAX_INTENTOS:
        await send_message(phone_number, DEMASIADOS_INTENTOS)
    else:
        await send_message(phone_number, error_msg)


# ---------------------------------------------------------------------------
# Completion
# ---------------------------------------------------------------------------


async def _complete_onboarding(phone_number: str, datos: dict) -> None:
    """Crea todos los registros en DB y envía mensaje de confirmación."""
    client = get_client()

    usuario_result = await asyncio.to_thread(
        lambda: client.table("usuarios").insert({
            "phone_number": phone_number,
            "nombre": datos["nombre"],
        }).execute()
    )
    usuario_id = usuario_result.data[0]["id"]

    await asyncio.to_thread(
        lambda: client.table("perfiles").insert({
            "usuario_id": usuario_id,
            "edad": datos["edad"],
            "peso_kg": datos["peso_kg"],
            "talla_cm": datos["talla_cm"],
            "genero": datos["genero"],
            "meta": datos["meta"],
            "alergias": datos.get("alergias", "ninguna"),
        }).execute()
    )

    await asyncio.to_thread(
        lambda: client.table("consentimientos").insert({
            "usuario_id": usuario_id,
            "acepto": True,
        }).execute()
    )

    await _delete_state(phone_number)
    await send_message(phone_number, onboarding_completo(datos["nombre"]))
    logger.info(f"Onboarding completado para {phone_number} (usuario_id={usuario_id}) — pendiente US-003")


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _validate_answer(paso: int, text: str) -> tuple[bool, object, str | None]:
    """Retorna (es_valido, valor_parseado, codigo_error)."""
    if paso == 1:
        nombre = text.strip()
        return (True, nombre.title(), None) if nombre else (False, None, "invalid")

    if paso == 2:
        match = re.search(r"\d+", text)
        if not match:
            return False, None, "invalid"
        edad = int(match.group())
        if edad < 13:
            return False, None, "edad_minima"
        return (True, edad, None) if edad <= 120 else (False, None, "invalid")

    if paso == 3:
        match = re.search(r"(\d+(?:[.,]\d+)?)", text)
        if not match:
            return False, None, "invalid"
        peso = float(match.group(1).replace(",", "."))
        if 20 <= peso <= 400:
            return True, peso, None
        return False, peso, "peso_fuera_de_rango"

    if paso == 4:
        match = re.search(r"\d+", text)
        if not match:
            return False, None, "invalid"
        talla = int(match.group())
        return (True, talla, None) if 100 <= talla <= 250 else (False, None, "invalid")

    if paso == 5:
        genero = text.strip()
        return (True, genero, None) if genero in _GENEROS else (False, None, "invalid")

    if paso == 6:
        meta = _METAS.get(text.strip())
        return (True, meta, None) if meta else (False, None, "invalid")

    if paso == 7:
        alergias = text.strip()
        return (True, alergias, None) if alergias else (False, None, "invalid")

    return False, None, "invalid"


def _save_answer(paso: int, value: object, datos: dict) -> dict:
    keys = {1: "nombre", 2: "edad", 3: "peso_kg", 4: "talla_cm",
            5: "genero", 6: "meta", 7: "alergias"}
    datos[keys[paso]] = value
    return datos


def _normalize(text: str) -> str:
    """Lowercase y normaliza variantes sin acentos para comparaciones."""
    result = text.lower().strip()
    for accented, plain in [("á","a"),("é","e"),("í","i"),("ó","o"),("ú","u"),("ü","u"),("ñ","n")]:
        result = result.replace(accented, plain)
    return result


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------


async def _load_state(phone_number: str) -> dict | None:
    client = get_client()
    result = await asyncio.to_thread(
        lambda: client.table("onboarding_estado")
            .select("*")
            .eq("phone_number", phone_number)
            .execute()
    )
    return result.data[0] if result.data else None


async def _create_state(phone_number: str) -> None:
    client = get_client()
    await asyncio.to_thread(
        lambda: client.table("onboarding_estado").insert({
            "phone_number": phone_number,
            "paso_actual": 0,
            "datos_parciales": {},
            "intentos_paso": 0,
        }).execute()
    )


async def _save_state(
    phone_number: str, paso: int, datos: dict, intentos: int
) -> None:
    client = get_client()
    await asyncio.to_thread(
        lambda: client.table("onboarding_estado").update({
            "paso_actual": paso,
            "datos_parciales": datos,
            "intentos_paso": intentos,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("phone_number", phone_number).execute()
    )


async def _delete_state(phone_number: str) -> None:
    client = get_client()
    await asyncio.to_thread(
        lambda: client.table("onboarding_estado")
            .delete()
            .eq("phone_number", phone_number)
            .execute()
    )
