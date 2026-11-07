"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: str = "postgresql+psycopg2://internradar:internradar@localhost:5432/internradar"

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    REQUEST_TIMEOUT: int = 30
    MAX_CONCURRENT_REQUESTS: int = 5
    USER_AGENT: str = "InternRadar/0.1 (+https://internradar.example.com)"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()