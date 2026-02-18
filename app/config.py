from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

ROOT_DIR = Path(__file__).resolve().parent.parent


def _load_env_files() -> str:
    base_env = ROOT_DIR / ".env"
    if base_env.exists():
        load_dotenv(base_env, override=False)

    app_env = os.getenv("APP_ENV", "production").strip().lower() or "production"
    mode_env = ROOT_DIR / f".env.{app_env}"
    if mode_env.exists():
        load_dotenv(mode_env, override=True)

    return app_env


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Settings(BaseModel):
    app_name: str
    app_env: Literal["development", "production"]
    host: str
    port: int
    debug: bool
    database_url: str


@lru_cache
def get_settings() -> Settings:
    app_env = _load_env_files()
    try:
        return Settings(
            app_name=os.getenv("APP_NAME", "Fast Lego"),
            app_env="development" if app_env == "development" else "production",
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
            debug=_as_bool(os.getenv("DEBUG"), default=False),
            database_url=os.getenv(
                "DATABASE_URL",
                "postgresql+psycopg://postgres:postgres@db:5432/fast_lego",
            ),
        )
    except ValidationError as exc:
        raise RuntimeError(f"Invalid configuration: {exc}") from exc


settings = get_settings()
