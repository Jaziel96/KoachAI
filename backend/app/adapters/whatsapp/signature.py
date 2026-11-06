"""Validación de la firma HMAC de los webhooks de Meta (US-016, RF-3)."""

from __future__ import annotations

import hashlib
import hmac

_PREFIX = "sha256="


def verify_signature(body: bytes, signature_header: str | None, app_secret: str) -> bool:
    """Valida `X-Hub-Signature-256` contra el HMAC-SHA256 del cuerpo crudo.

    Usa `hmac.compare_digest` para no filtrar información por tiempo de respuesta.
    """
    if not signature_header or not signature_header.startswith(_PREFIX):
        return False
    esperado = hmac.new(app_secret.encode(), body, hashlib.sha256).hexdigest()
    recibido = signature_header.removeprefix(_PREFIX)
    return hmac.compare_digest(esperado.encode(), recibido.encode())
