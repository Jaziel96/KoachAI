"""Tests de US-005: inicialización de Sentry y filtrado determinista de PII."""

from typing import Any

from app.core.config import Settings
from app.core.sentry import init_sentry, scrub_pii


def _settings(**overrides: Any) -> Settings:
    return Settings(
        DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/koach_test",  # type: ignore[arg-type]
        SUPABASE_URL="https://example.supabase.co",  # type: ignore[arg-type]
        SUPABASE_SERVICE_KEY="test-service-key",  # type: ignore[arg-type]
        REDIS_URL="redis://localhost:6379/0",  # type: ignore[arg-type]
        WHATSAPP_TOKEN="test-token",  # type: ignore[arg-type]
        WHATSAPP_PHONE_NUMBER_ID="123456",
        WHATSAPP_VERIFY_TOKEN="test-verify-token",  # type: ignore[arg-type]
        **overrides,
    )


def test_init_sentry_noop_sin_dsn() -> None:
    """Sin SENTRY_DSN, init_sentry no debe lanzar ni requerir red."""
    init_sentry(_settings(SENTRY_DSN=None))


def test_scrub_pii_enmascara_telefono_mexicano() -> None:
    event: dict[str, Any] = {"message": "Error al notificar a +525512345678"}

    result = scrub_pii(event, {})  # type: ignore[arg-type]

    assert result is not None
    assert result["message"] == "Error al notificar a +52****5678"


def test_scrub_pii_elimina_datos_de_salud_del_usuario() -> None:
    event: dict[str, Any] = {
        "user": {
            "id": "user-123",
            "nombre": "Juan Pérez",
            "peso": 78.5,
            "imc": 24.1,
        }
    }

    result = scrub_pii(event, {})  # type: ignore[arg-type]

    assert result is not None
    assert result["user"] == {"id": "user-123"}


def test_scrub_pii_enmascara_telefono_en_extra_y_contexto() -> None:
    event: dict[str, Any] = {
        "extra": {"telefono_contacto": "+525587654321"},
        "contexts": {"whatsapp": {"phone": "+525511112222"}},
    }

    result = scrub_pii(event, {})  # type: ignore[arg-type]

    assert result is not None
    assert result["extra"]["telefono_contacto"] == "+52****4321"
    assert "phone" not in result["contexts"]["whatsapp"]


def test_scrub_pii_no_altera_evento_sin_pii() -> None:
    event: dict[str, Any] = {
        "message": "Timeout conectando a la base de datos",
        "extra": {"request_id": "abc-123", "status_code": 500},
    }

    result = scrub_pii(dict(event), {})  # type: ignore[arg-type]

    assert result == event
