"""Tests de validación de firma HMAC del webhook (US-016, RF-3)."""

import hashlib
import hmac

from app.adapters.whatsapp.signature import verify_signature

SECRET = "app-secret"
BODY = b'{"object":"whatsapp_business_account"}'


def _firma(body: bytes, secret: str = SECRET) -> str:
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def test_firma_valida() -> None:
    assert verify_signature(BODY, _firma(BODY), SECRET)


def test_firma_con_secreto_incorrecto() -> None:
    assert not verify_signature(BODY, _firma(BODY, "otro"), SECRET)


def test_firma_con_cuerpo_alterado() -> None:
    assert not verify_signature(BODY + b" ", _firma(BODY), SECRET)


def test_firma_ausente_o_malformada() -> None:
    assert not verify_signature(BODY, None, SECRET)
    assert not verify_signature(BODY, "", SECRET)
    assert not verify_signature(BODY, "md5=abc", SECRET)
    assert not verify_signature(BODY, "sha256=ñññ", SECRET)
