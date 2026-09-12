"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────
    app_name: str = "Elevator AI"
    app_version: str = "0.1.0"
    debug: bool = False
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # ── Database ─────────────────────────────────────────
    database_url: str = Field(
        default="postgresql+asyncpg://elevator_user:elevator_pass@localhost:5432/elevator_ai"
    )
    database_url_sync: str = Field(
        default="postgresql://elevator_user:elevator_pass@localhost:5432/elevator_ai"
    )

    # ── JWT ──────────────────────────────────────────────
    jwt_secret_key: str = Field(default="change-this-to-a-random-64-char-secret")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # ── Seed ─────────────────────────────────────────────
    admin_email: str = "mohan@elevatorai.io"
    admin_password: str = "change-this-password"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if not self.debug:
            insecure_jwt_fallbacks = {
                "change-this-to-a-random-64-char-secret",
                "secret",
                "change-me",
            }
            insecure_admin_passwords = {
                "change-this-password",
                "password",
                "admin",
            }
            if self.jwt_secret_key in insecure_jwt_fallbacks:
                raise ValueError(
                    "Production mode (DEBUG=false) requires a non-default JWT_SECRET_KEY environment variable."
                )
            if self.admin_password in insecure_admin_passwords:
                raise ValueError(
                    "Production mode (DEBUG=false) requires a non-default ADMIN_PASSWORD environment variable."
                )
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def normalized_database_url(self) -> str:
        url = self.database_url
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        if url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @property
    def normalized_database_url_sync(self) -> str:
        # Derive sync URL directly from database_url for Alembic compatibility
        url = self.database_url
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql://", 1)
        if url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql+asyncpg://", "postgresql://", 1)
        if url.startswith("postgresql://"):
            return url
        return self.database_url_sync


@lru_cache
def get_settings() -> Settings:
    return Settings()

