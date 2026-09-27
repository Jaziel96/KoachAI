"""Inicialización de Sentry y filtrado determinista de PII (US-005).

Requisito de seguridad (RF-4/CA-2/CA-3): ningún dato de salud ni teléfono sin
enmascarar debe llegar a Sentry. El filtrado corre en código (`before_send`),
nunca se confía en la configuración del SDK para hacerlo por su cuenta.
"""

import re
from typing import Any

import sentry_sdk
from sentry_sdk.types import Event, Hint

from app.core.config import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Teléfonos mexicanos en los formatos que realmente llegan: "+525512345678",
# "+5215512345678" y el `wa_id` de WhatsApp Cloud API, que viene SIN "+"
# ("5215512345678"). Se exige que no haya más dígitos pegados antes/después
# para no enmascarar identificadores largos que no son teléfonos.
_PHONE_PATTERN = re.compile(r"(?<!\d)(\+?52)1?\d{6}(\d{4})(?!\d)")

# Claves (como token completo, separado por "_") cuyo valor nunca debe salir.
# Se compara por token y no por subcadena para no romper campos técnicos como
# `filename` del stacktrace.
_SENSITIVE_KEY_PATTERN = re.compile(
    r"(^|_)(nombre|name|first_name|last_name|email|peso|weight|"
    r"talla|altura|height|imc|bmi|condiciones?|medical|alergias?|lesiones?|"
    r"medicamentos?|calorias?)(_|$)",
    re.IGNORECASE,
)

# Claves que son, por sí mismas, un teléfono: se eliminan. Cualquier otra clave
# con un teléfono en su valor (p. ej. `telefono_contacto`) se conserva pero
# enmascarada, para que el reporte siga siendo depurable (CA-3).
_PHONE_KEY_PATTERN = re.compile(r"^(phone|telefono|wa_id)$", re.IGNORECASE)

# Secciones del evento de Sentry que se filtran. `sdk`, `platform`, `event_id`,
# `timestamp`, etc. son metadatos técnicos y se dejan intactos.
_SCRUBBED_SECTIONS = (
    "user",
    "extra",
    "contexts",
    "tags",
    "request",
    "breadcrumbs",
    "exception",
    "logentry",
    "message",
)


def _mask_phones(value: str) -> str:
    """Reemplaza cualquier teléfono mexicano en `value` por `+52****XXXX`."""
    return _PHONE_PATTERN.sub(lambda m: f"{m.group(1)}****{m.group(2)}", value)


def _scrub_value(value: Any) -> Any:
    """Aplica el filtrado recursivamente sobre strings, dicts y listas."""
    if isinstance(value, str):
        return _mask_phones(value)
    if isinstance(value, dict):
        return _scrub_dict(value)
    if isinstance(value, list):
        return [_scrub_value(item) for item in value]
    return value


def _scrub_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Elimina claves de PII/salud y enmascara teléfonos en el resto."""
    return {
        key: _scrub_value(value)
        for key, value in data.items()
        if not _SENSITIVE_KEY_PATTERN.search(key) and not _PHONE_KEY_PATTERN.match(key)
    }


def _drop_frame_vars(event: Event) -> None:
    """Elimina las variables locales de cada frame del stacktrace.

    Los nombres de variables locales no son predecibles (`w`, `x`, `tmp`...), así
    que no se pueden filtrar por clave: para datos de salud lo seguro es no
    enviarlas nunca.
    """
    for exc in (event.get("exception") or {}).get("values", []):
        for frame in (exc.get("stacktrace") or {}).get("frames", []):
            frame.pop("vars", None)


def scrub_pii(event: Event, hint: Hint) -> Event | None:
    """Hook `before_send`: enmascara teléfonos y elimina PII/datos de salud."""
    _drop_frame_vars(event)
    for section in _SCRUBBED_SECTIONS:
        if section in event:
            event[section] = _scrub_value(event[section])  # type: ignore[literal-required]
    return event


def init_sentry(settings: Settings) -> None:
    """Inicializa el SDK de Sentry si `SENTRY_DSN` está configurado."""
    if not settings.SENTRY_DSN:
        logger.info("sentry_disabled", reason="SENTRY_DSN no configurado")
        return

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        before_send=scrub_pii,
        send_default_pii=False,
        include_local_variables=False,
    )
    logger.info("sentry_enabled", environment=settings.ENVIRONMENT)
