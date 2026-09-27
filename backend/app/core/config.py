"""Configuración de la aplicación vía variables de entorno.

Toda la configuración pasa por esta clase (Pydantic Settings). Nunca
hardcodear secretos ni URLs en el código — ver regla #3 de CLAUDE.md.
"""

from functools import lru_cache
from typing import Literal

from pydantic import HttpUrl, PostgresDsn, RedisDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la aplicación, cargada desde variables de entorno."""

    # App
    APP_NAME: str = "Koach"
    ENVIRONMENT: Literal["dev", "staging", "prod"] = "dev"
    DEBUG: bool = False

    # Database
    DATABASE_URL: PostgresDsn
    SUPABASE_URL: HttpUrl
    SUPABASE_SERVICE_KEY: SecretStr

    # Redis
    REDIS_URL: RedisDsn

    # AI
    AI_STRATEGY: Literal["api", "hybrid", "local"] = "api"
    AI_SMART_PROVIDER: str = "anthropic"
    AI_FAST_PROVIDER: str = "gemini"
    ANTHROPIC_API_KEY: SecretStr | None = None
    GEMINI_API_KEY: SecretStr | None = None

    # WhatsApp
    WHATSAPP_TOKEN: SecretStr
    WHATSAPP_PHONE_NUMBER_ID: str
    WHATSAPP_VERIFY_TOKEN: SecretStr

    # HTTP
    CORS_ALLOWED_ORIGINS: list[str] = []

    # Observabilidad
    SENTRY_DSN: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Retorna la instancia cacheada de Settings.

    Usar esta función (no instanciar Settings directamente) para permitir
    inyección de dependencias y evitar releer el .env en cada llamada.
    """
    return Settings()
