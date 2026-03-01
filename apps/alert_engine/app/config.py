from __future__ import annotations

import os
from dataclasses import dataclass


def _as_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    request_timeout_seconds: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "4.0"))

    telnyx_api_key: str = os.getenv("TELNYX_API_KEY", "")
    telnyx_from: str = os.getenv("TELNYX_FROM", "")
    telnyx_to: str = os.getenv("TELNYX_TO", "")
    telnyx_messaging_profile_id: str = os.getenv("TELNYX_MESSAGING_PROFILE_ID", "")

    auto_dispatch_sms: bool = _as_bool(os.getenv("AUTO_DISPATCH_SMS", "false"), default=False)


settings = Settings()
