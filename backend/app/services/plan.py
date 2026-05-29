import asyncio
import logging
import time

from app.db.supabase import get_client
from app.messages.es_mx import ERROR_GENERANDO_PLAN
from app.prompts.plan_inicial import construir_prompt
from app.services.claude import generate_plan
from app.services.whatsapp_sender import send_message

logger = logging.getLogger(__name__)

_MAX_CHUNK_CHARS = 1500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def generar_plan_inicial(phone_number: str) -> None:
    """Recupera el perfil, llama a Claude, guarda el plan y lo envía al usuario."""
    inicio = time.monotonic()

    try:
        perfil = await _recuperar_perfil(phone_number)
        if not perfil:
            logger.error(f"Perfil no encontrado para {phone_number} al generar plan — CE-01")
            return

        tmb, tdee = calcular_tdee(
            peso_kg=float(perfil["peso_kg"]),
            talla_cm=perfil["talla_cm"],
            edad=perfil["edad"],
            genero=perfil["genero"],
        )
        meta_calorica = calcular_meta_calorica(tdee, perfil["meta"])

        prompt = construir_prompt(
            nombre=perfil["nombre"],
            edad=perfil["edad"],
            peso_kg=float(perfil["peso_kg"]),
            talla_cm=perfil["talla_cm"],
            genero=perfil["genero"],
            meta=perfil["meta"],
            alergias=perfil.get("alergias", "ninguna"),
            tmb=tmb,
            tdee=tdee,
            meta_calorica=meta_calorica,
        )

        try:
            plan_texto = await generate_plan(prompt)
        except Exception as exc:
            logger.error(f"Claude API falló tras reintento para {phone_number}: {exc}")
            await send_message(phone_number, ERROR_GENERANDO_PLAN)
            return

        duracion = round(time.monotonic() - inicio, 2)
        await _guardar_plan(
            usuario_id=perfil["usuario_id"],
            contenido=plan_texto,
            tmb=tmb,
            tdee=tdee,
            meta_calorica=meta_calorica,
            duracion=duracion,
        )

        chunks = _chunk_message(plan_texto)
        for chunk in chunks:
            await send_message(phone_number, chunk)
            await asyncio.sleep(1)

        logger.info(f"Plan enviado a {phone_number} en {duracion}s — {len(chunks)} mensajes")

    except Exception as exc:
        logger.error(f"Error crítico en generar_plan_inicial para {phone_number}: {exc}")
        await send_message(phone_number, ERROR_GENERANDO_PLAN)


# ---------------------------------------------------------------------------
# Cálculos nutricionales
# ---------------------------------------------------------------------------


def calcular_tdee(
    peso_kg: float, talla_cm: int, edad: int, genero: str
) -> tuple[float, float]:
    """Retorna (TMB, TDEE) con Mifflin-St Jeor y factor sedentario 1.2."""
    tmb_h = 10 * peso_kg + 6.25 * talla_cm - 5 * edad + 5
    tmb_m = 10 * peso_kg + 6.25 * talla_cm - 5 * edad - 161

    if genero == "hombre":
        tmb = tmb_h
    elif genero == "mujer":
        tmb = tmb_m
    else:
        tmb = (tmb_h + tmb_m) / 2

    return tmb, tmb * 1.2


def calcular_meta_calorica(tdee: float, meta: str) -> float:
    """Ajusta el TDEE según la meta del usuario."""
    ajustes: dict[str, float] = {
        "bajar de peso": -300.0,
        "ganar músculo": 250.0,
    }
    return tdee + ajustes.get(meta, 0.0)


# ---------------------------------------------------------------------------
# Chunker
# ---------------------------------------------------------------------------


def _chunk_message(text: str, max_chars: int = _MAX_CHUNK_CHARS) -> list[str]:
    """Divide texto en chunks de hasta max_chars, cortando en dobles saltos de línea."""
    if len(text) <= max_chars:
        return [text]

    chunks: list[str] = []
    while len(text) > max_chars:
        cut_pos = text.rfind("\n\n", 0, max_chars)
        if cut_pos != -1:
            chunk, text = text[:cut_pos + 2], text[cut_pos + 2:]
        else:
            chunk, text = text[:max_chars], text[max_chars:]
        if chunk.strip():
            chunks.append(chunk.strip())

    if text.strip():
        chunks.append(text.strip())

    return chunks


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------


async def _recuperar_perfil(phone_number: str) -> dict | None:
    """Recupera usuario + perfil completo desde Supabase."""
    client = get_client()

    user_result = await asyncio.to_thread(
        lambda: client.table("usuarios")
            .select("id,nombre")
            .eq("phone_number", phone_number)
            .execute()
    )
    if not user_result.data:
        return None

    usuario = user_result.data[0]

    perfil_result = await asyncio.to_thread(
        lambda: client.table("perfiles")
            .select("*")
            .eq("usuario_id", usuario["id"])
            .execute()
    )
    if not perfil_result.data:
        return None

    return {**perfil_result.data[0], "nombre": usuario["nombre"], "usuario_id": usuario["id"]}


async def _guardar_plan(
    usuario_id: str,
    contenido: str,
    tmb: float,
    tdee: float,
    meta_calorica: float,
    duracion: float,
) -> None:
    """Guarda el plan en Supabase. CE-03: si falla, loggea y continúa."""
    try:
        client = get_client()
        await asyncio.to_thread(
            lambda: client.table("planes").insert({
                "usuario_id": usuario_id,
                "contenido": contenido,
                "tmb": round(tmb, 2),
                "tdee": round(tdee, 2),
                "meta_calorica": round(meta_calorica, 2),
                "generado_en": duracion,
            }).execute()
        )
    except Exception as exc:
        logger.error(f"Error guardando plan en DB para usuario {usuario_id}: {exc} — CE-03")
