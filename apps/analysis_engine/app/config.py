from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    request_timeout_seconds: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "4.0"))

    hume_api_key: str = os.getenv("HUME_API_KEY", "")
    hume_api_url: str = os.getenv("HUME_API_URL", "")

    langaware_api_key: str = os.getenv("LANGAWARE_API_KEY", "")
    langaware_api_url: str = os.getenv("LANGAWARE_API_URL", "")


settings = Settings()
