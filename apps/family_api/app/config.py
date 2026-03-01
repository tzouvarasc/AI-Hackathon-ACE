from __future__ import annotations

import os
from dataclasses import dataclass


def _to_int(value: str, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return default


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://thalpo:thalpo@localhost:5432/thalpo",
    )
    jwt_secret: str = os.getenv("JWT_SECRET", "change-me-in-prod")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expires_minutes: int = _to_int(os.getenv("JWT_EXPIRES_MINUTES", "120"), 120)

    internal_service_token: str = os.getenv("INTERNAL_SERVICE_TOKEN", "thalpo-internal-dev")

    bootstrap_admin_username: str = os.getenv("BOOTSTRAP_ADMIN_USERNAME", "admin")
    bootstrap_admin_password: str = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "admin123")
    bootstrap_admin_display_name: str = os.getenv("BOOTSTRAP_ADMIN_DISPLAY_NAME", "Thalpo Admin")

    cors_origins: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
