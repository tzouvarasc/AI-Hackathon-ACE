from __future__ import annotations

import asyncio
import json
import os
import time
from uuid import uuid4

import httpx

try:  # pragma: no cover - optional dependency resolution
    from google.cloud import texttospeech
    from google.oauth2 import service_account
except Exception:  # pragma: no cover
    texttospeech = None  # type: ignore[assignment]
    service_account = None  # type: ignore[assignment]


class TTSProvider:
    """Multi-backend TTS provider with Google Chirp-3/Leda support first."""

    def __init__(
        self,
        backend: str,
        output_dir: str,
        timeout_seconds: float,
        cartesia_api_key: str,
        cartesia_voice_id: str,
        cartesia_model_id: str,
        google_language_code: str,
        google_voice_name: str,
        google_credentials_json: str,
        google_speaking_rate: float,
    ) -> None:
        self.backend = (backend or "google").strip().lower()
        self.output_dir = output_dir
        self.timeout_seconds = timeout_seconds

        self.cartesia_api_key = cartesia_api_key
        self.cartesia_voice_id = cartesia_voice_id
        self.cartesia_model_id = cartesia_model_id

        self.google_language_code = google_language_code
        self.google_voice_name = google_voice_name
        self.google_credentials_json = google_credentials_json
        self.google_speaking_rate = google_speaking_rate
        self.google_client = self._build_google_client()

    def _build_google_client(self):
        if texttospeech is None:
            return None

        if self.google_credentials_json and service_account is not None:
            try:
                credentials_data = json.loads(self.google_credentials_json)
                credentials = service_account.Credentials.from_service_account_info(credentials_data)
                return texttospeech.TextToSpeechClient(credentials=credentials)
            except Exception as exc:  # pragma: no cover - runtime credentials path
                print(f"[tts] Google JSON credentials parse failed: {exc}")

        try:
            return texttospeech.TextToSpeechClient()
        except Exception as exc:  # pragma: no cover - runtime credentials path
            print(f"[tts] Google TTS client init failed: {exc}")
            return None

    def _backend_order(self) -> list[str]:
        if self.backend == "google":
            return ["google", "cartesia"]
        if self.backend == "cartesia":
            return ["cartesia", "google"]
        return ["google", "cartesia"]

    async def synthesize(self, text: str, session_id: str) -> tuple[str, int]:
        start = time.perf_counter()
        chunk_id = uuid4().hex[:10]

        for backend_name in self._backend_order():
            audio_bytes = None
            if backend_name == "google":
                audio_bytes = await self._synthesize_google(text)
            elif backend_name == "cartesia":
                audio_bytes = await self._synthesize_cartesia(text)

            if audio_bytes:
                os.makedirs(self.output_dir, exist_ok=True)
                filepath = os.path.join(self.output_dir, f"{session_id}-{chunk_id}.mp3")
                with open(filepath, "wb") as file_obj:
                    file_obj.write(audio_bytes)

                elapsed_ms = int((time.perf_counter() - start) * 1000)
                return f"file://{filepath}", max(elapsed_ms, 80)

        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return f"stream://{session_id}/{chunk_id}", max(elapsed_ms, 80)

    async def _synthesize_google(self, text: str) -> bytes | None:
        if not self.google_client or texttospeech is None:
            return None

        def run_sync() -> bytes | None:
            try:
                response = self.google_client.synthesize_speech(
                    input=texttospeech.SynthesisInput(text=text),
                    voice=texttospeech.VoiceSelectionParams(
                        language_code=self.google_language_code,
                        name=self.google_voice_name,
                    ),
                    audio_config=texttospeech.AudioConfig(
                        audio_encoding=texttospeech.AudioEncoding.MP3,
                        speaking_rate=self.google_speaking_rate,
                    ),
                )
                return bytes(response.audio_content)
            except Exception as exc:  # pragma: no cover - integration path
                print(f"[tts] Google synthesis failed: {exc}")
                return None

        return await asyncio.to_thread(run_sync)

    async def _synthesize_cartesia(self, text: str) -> bytes | None:
        if not self.cartesia_api_key or not self.cartesia_voice_id:
            return None

        payload = {
            "model_id": self.cartesia_model_id,
            "transcript": text,
            "voice": {"mode": "id", "id": self.cartesia_voice_id},
            "output_format": {
                "container": "mp3",
                "encoding": "mp3",
                "sample_rate": 44100,
            },
        }
        headers = {
            "X-API-Key": self.cartesia_api_key,
            "Content-Type": "application/json",
            "Cartesia-Version": "2024-06-10",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    "https://api.cartesia.ai/tts/bytes",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                return bytes(response.content)
        except Exception as exc:  # pragma: no cover - integration path
            print(f"[tts] Cartesia synthesis failed: {exc}")
            return None
