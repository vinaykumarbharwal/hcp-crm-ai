from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Defaults make local development work even before a full .env is created.
    app_env: str = "local"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/hcp_crm_ai"
    groq_api_key: str = ""
    primary_model: str = "gemma2-9b-it"
    support_model: str = "llama-3.3-70b-versatile"
    allowed_origins: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()


