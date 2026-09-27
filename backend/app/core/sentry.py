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

_PHONE_PATTERN = re.compile(r"(\+52)(\d{6})(\d{4})")

_SENSITIVE_KEYS = frozenset(
    {
        "nombre",
        "name",
        "first_name",
        "last_name",
        "phone",
        "telefono",
        "peso",
        "weight",
        "altura",
        "height",
        "imc",
        "bmi",
        "condiciones_medicas",
        "medical_conditions",
        "email",
    }
)


def _mask_phones(value: str) -> str:
    """Reemplaza cualquier teléfono mexicano en `value` por `+52****XXXX`."""
    return _PHONE_PATTERN.sub(lambda m: f"{m.group(1)}****{m.group(3)}", value)


def _scrub_value(value: Any) -> Any:
    """Aplica enmascarado de teléfonos recursivamente sobre strings, dicts y listas."""
    if isinstance(value, str):
        return _mask_phones(value)
    if isinstance(value, dict):
        return _scrub_dict(value)
    if isinstance(value, list):
        return [_scrub_value(item) for item in value]
    return value


def _scrub_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Elimina claves de PII/salud conocidas y enmascara teléfonos en el resto."""
    scrubbed: dict[str, Any] = {}
    for key, value in data.items():
        if key.lower() in _SENSITIVE_KEYS:
            continue
        scrubbed[key] = _scrub_value(value)
    return scrubbed


def scrub_pii(event: Event, hint: Hint) -> Event | None:
    """Hook `before_send`: enmascara teléfonos y elimina PII/datos de salud."""
    if "user" in event and isinstance(event["user"], dict):
        event["user"] = _scrub_dict(event["user"])

    if "extra" in event and isinstance(event["extra"], dict):
        event["extra"] = _scrub_dict(event["extra"])

    if "contexts" in event and isinstance(event["contexts"], dict):
        event["contexts"] = {
            ctx_key: _scrub_dict(ctx_value) if isinstance(ctx_value, dict) else ctx_value
            for ctx_key, ctx_value in event["contexts"].items()
        }

    if event.get("message"):
        event["message"] = _mask_phones(event["message"])

    for exc in event.get("exception", {}).get("values", []) if event.get("exception") else []:
        if exc.get("value"):
            exc["value"] = _mask_phones(exc["value"])

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
    )
    logger.info("sentry_enabled", environment=settings.ENVIRONMENT)
