from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    anthropic_api_key: str = ""
    supabase_url: str = ""
    supabase_key: str = ""
    whatsapp_token: str = ""
    whatsapp_verify_token: str


settings = Settings()
