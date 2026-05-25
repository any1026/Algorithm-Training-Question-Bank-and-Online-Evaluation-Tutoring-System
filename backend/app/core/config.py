from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Algorithm Training API"
    app_env: str = "local"
    app_debug: bool = True
    database_url: str = "sqlite:///./tmp/oj_training.db"
    redis_url: str = "redis://localhost:6380/0"
    judge_workspace: Path = Path("./tmp/judge")
    judge_time_limit_seconds: int = Field(default=2, ge=1, le=10)
    judge_memory_limit_mb: int = Field(default=256, ge=64, le=2048)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
