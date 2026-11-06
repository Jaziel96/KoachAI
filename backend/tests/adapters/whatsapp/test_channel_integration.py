"""CA-1 de US-017: el mensaje llega al WhatsApp del usuario (API real de Meta).

Se omite sin credenciales propias de integración. Ejecutar solo estos:
    pytest -m integration -v
Requiere: KOACH_WA_IT_TOKEN, KOACH_WA_IT_PHONE_NUMBER_ID, KOACH_WA_IT_API_VERSION y
KOACH_WA_IT_TO (un teléfono de prueba registrado en el sandbox de Meta). Son
variables distintas de las `WHATSAPP_*` para no enviar mensajes reales por accidente.
"""

import os

import pytest

from app.adapters.whatsapp.channel import WhatsAppChannel

pytestmark = pytest.mark.integration

_VARS = (
    "KOACH_WA_IT_TOKEN",
    "KOACH_WA_IT_PHONE_NUMBER_ID",
    "KOACH_WA_IT_API_VERSION",
    "KOACH_WA_IT_TO",
)


@pytest.mark.skipif(
    not all(os.environ.get(v) for v in _VARS),
    reason="faltan credenciales de integración de WhatsApp (KOACH_WA_IT_*)",
)
async def test_ca1_el_mensaje_llega_a_whatsapp() -> None:
    canal = WhatsAppChannel(
        token=os.environ["KOACH_WA_IT_TOKEN"],
        phone_number_id=os.environ["KOACH_WA_IT_PHONE_NUMBER_ID"],
        api_version=os.environ["KOACH_WA_IT_API_VERSION"],
    )
    message_id = await canal.send_text(os.environ["KOACH_WA_IT_TO"], "Prueba de integración Koach")
    assert message_id.startswith("wamid.")
