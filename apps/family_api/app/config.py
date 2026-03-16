from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field

_WEAK_JWT = "change-me-in-prod"
_WEAK_ADMIN_PASSWORD = "admin123"
_WEAK_INTERNAL_TOKEN = "thalpo-internal-dev"


def _to_int(value: str, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _warn(msg: str) -> None:
    print(f"[family-api][SECURITY WARNING] {msg}", file=sys.stderr, flush=True)


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://thalpo:thalpo@localhost:5432/thalpo",
    )
    jwt_secret: str = os.getenv("JWT_SECRET", _WEAK_JWT)
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expires_minutes: int = _to_int(os.getenv("JWT_EXPIRES_MINUTES", "120"), 120)

    internal_service_token: str = os.getenv("INTERNAL_SERVICE_TOKEN", _WEAK_INTERNAL_TOKEN)

    bootstrap_admin_username: str = os.getenv("BOOTSTRAP_ADMIN_USERNAME", "admin")
    bootstrap_admin_password: str = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", _WEAK_ADMIN_PASSWORD)
    bootstrap_admin_display_name: str = os.getenv("BOOTSTRAP_ADMIN_DISPLAY_NAME", "Thalpo Admin")

    cors_origins: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def validate_security(self) -> None:
        """Emit warnings for any insecure default values still in use."""
        if self.jwt_secret == _WEAK_JWT:
            _warn("JWT_SECRET is using the insecure default. Set a strong secret via JWT_SECRET env var.")
        if self.bootstrap_admin_password == _WEAK_ADMIN_PASSWORD:
            _warn("BOOTSTRAP_ADMIN_PASSWORD is using the insecure default 'admin123'. Set BOOTSTRAP_ADMIN_PASSWORD.")
        if self.internal_service_token == _WEAK_INTERNAL_TOKEN:
            _warn("INTERNAL_SERVICE_TOKEN is using the insecure default. Set INTERNAL_SERVICE_TOKEN.")


settings = Settings()
settings.validate_security()
