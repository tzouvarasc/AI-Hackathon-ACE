from __future__ import annotations

import time

import httpx


class STTProvider:
    """Deepgram-backed STT with text fallback for local development."""

    def __init__(
        self,
        api_key: str,
        model: str,
        language: str,
        timeout_seconds: float,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.language = language
        self.timeout_seconds = timeout_seconds

    async def transcribe(self, raw_text: str, audio_url: str | None = None) -> tuple[str, int]:
        start = time.perf_counter()

        if raw_text.strip():
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            return raw_text.strip(), max(elapsed_ms, 120)

        if not audio_url or not self.api_key:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            return "", max(elapsed_ms, 120)

        headers = {"Authorization": f"Token {self.api_key}"}
        params = {
            "model": self.model,
            "language": self.language,
            "smart_format": "true",
        }
        body = {"url": audio_url}

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    "https://api.deepgram.com/v1/listen",
                    params=params,
                    headers=headers,
                    json=body,
                )
                response.raise_for_status()
                payload = response.json()

            transcript = (
                payload.get("results", {})
                .get("channels", [{}])[0]
                .get("alternatives", [{}])[0]
                .get("transcript", "")
                .strip()
            )
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            return transcript, max(elapsed_ms, 120)
        except Exception as exc:  # pragma: no cover - integration path
            print(f"[stt] Deepgram transcribe failed: {exc}")
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            return "", max(elapsed_ms, 120)
