from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./legal_agent.db"
    db_echo: bool = False
    # Comma-separated allowed API keys. Empty = auth disabled (dev only).
    api_keys: str = ""
    upload_dir: str = "./uploads"
    max_upload_mb: int = 10

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
