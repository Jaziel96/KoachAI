"""Configuración de la aplicación vía variables de entorno.

Toda la configuración pasa por esta clase (Pydantic Settings). Nunca
hardcodear secretos ni URLs en el código — ver regla #3 de CLAUDE.md.
"""

from functools import lru_cache
from typing import Literal

from pydantic import BaseModel, HttpUrl, PostgresDsn, RedisDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ModelPricing(BaseModel):
    """Precio de un modelo en USD por millón de tokens."""

    input_per_mtok: float
    output_per_mtok: float


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
    AI_FAST_PROVIDER: str = "anthropic"
    ANTHROPIC_API_KEY: SecretStr | None = None
    GEMINI_API_KEY: SecretStr | None = None
    ANTHROPIC_MODEL_FAST: str = "claude-haiku-4-5"
    ANTHROPIC_MODEL_SMART: str = "claude-sonnet-5"
    ANTHROPIC_MODEL_VISION: str = "claude-sonnet-5"
    ANTHROPIC_TIMEOUT_SECONDS: float = 30.0
    ANTHROPIC_MAX_RETRIES: int = 3
    ANTHROPIC_RETRY_AFTER_CAP_SECONDS: float = 30.0
    # Sin default a propósito: los precios cambian y deben confirmarse contra la
    # página oficial. Formato JSON: {"<modelo>": {"input_per_mtok": X, "output_per_mtok": Y}}
    ANTHROPIC_PRICING: dict[str, ModelPricing] = {}

    # WhatsApp
    WHATSAPP_TOKEN: SecretStr
    WHATSAPP_PHONE_NUMBER_ID: str
    WHATSAPP_VERIFY_TOKEN: SecretStr
    WHATSAPP_APP_SECRET: SecretStr
    # Sin default a propósito: la versión vigente de la Graph API debe confirmarse
    # contra la documentación de Meta (ej. "v<NN>.0").
    WHATSAPP_API_VERSION: str | None = None
    WHATSAPP_BASE_URL: str = "https://graph.facebook.com"
    WHATSAPP_TIMEOUT_SECONDS: float = 10.0
    WHATSAPP_MAX_RETRIES: int = 3

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
