"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Loads settings from environment variables or a .env file."""

    DATABASE_URL: str = "sqlite:///./addressbook.db"
    LOG_LEVEL: str = "INFO"
    APP_NAME: str = "Address Book API"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()