from __future__ import annotations

import httpx


class TelnyxNotifier:
    def __init__(
        self,
        api_key: str,
        from_number: str,
        to_number: str,
        messaging_profile_id: str,
        timeout_seconds: float,
    ) -> None:
        self.api_key = api_key
        self.from_number = from_number
        self.to_number = to_number
        self.messaging_profile_id = messaging_profile_id
        self.timeout_seconds = timeout_seconds

    async def send_sms(self, body: str) -> bool:
        if not all([self.api_key, self.to_number, body]):
            return False

        payload: dict[str, str] = {
            "to": self.to_number,
            "text": body,
        }

        if self.from_number:
            payload["from"] = self.from_number
        if self.messaging_profile_id:
            payload["messaging_profile_id"] = self.messaging_profile_id

        if "from" not in payload and "messaging_profile_id" not in payload:
            return False

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    "https://api.telnyx.com/v2/messages",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
            return True
        except Exception as exc:  # pragma: no cover - external API path
            print(f"[alert] Telnyx send failed: {exc}")
            return False
