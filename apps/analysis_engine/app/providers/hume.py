from __future__ import annotations

import httpx


class HumeProvider:
    """Hume adapter. Uses optional URL override for account-specific deployment."""

    def __init__(self, api_key: str, api_url: str, timeout_seconds: float) -> None:
        self.api_key = api_key
        self.api_url = api_url
        self.timeout_seconds = timeout_seconds

    async def analyze(self, transcript: str, audio_url: str | None = None) -> dict | None:
        if not self.api_key or not self.api_url or not transcript.strip():
            return None

        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "transcript": transcript,
            "audio_url": audio_url,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(self.api_url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
            return {
                "emotion_label": data.get("emotion_label"),
                "emotion_score": data.get("emotion_score"),
                "raw": data,
            }
        except Exception as exc:  # pragma: no cover - external API path
            print(f"[analysis:hume] request failed: {exc}")
            return None
