from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field("Listings API", alias="APP_NAME")
    app_env: str = Field("development", alias="APP_ENV")
    database_url: str = Field(..., alias="DATABASE_URL")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", env_prefix="")


settings = Settings()


def get_settings() -> Settings:
    """Return the shared settings instance."""

    return settings
