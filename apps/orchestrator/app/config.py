from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


_REPO_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(_REPO_ROOT / ".env", override=False)


def _as_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _as_float(value: str, default: float) -> float:
    try:
        return float(value)
    except Exception:
        return default


@dataclass(frozen=True)
class Settings:
    provider_mode: str = os.getenv("PROVIDER_MODE", "hybrid")
    public_base_url: str = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000")

    livekit_api_key: str = os.getenv("LIVEKIT_API_KEY", "")
    livekit_api_secret: str = os.getenv("LIVEKIT_API_SECRET", "")
    livekit_ws_url: str = os.getenv("LIVEKIT_WS_URL", "wss://your-livekit-host")
    livekit_sip_inbound_trunk_id: str = os.getenv("LIVEKIT_SIP_INBOUND_TRUNK_ID", "")
    livekit_sip_outbound_trunk_id: str = os.getenv("LIVEKIT_SIP_OUTBOUND_TRUNK_ID", "")
    livekit_sip_room_prefix: str = os.getenv("LIVEKIT_SIP_ROOM_PREFIX", "thalpo-pstn-")
    livekit_sip_dispatch_metadata: str = os.getenv("LIVEKIT_SIP_DISPATCH_METADATA", "")

    telnyx_api_key: str = os.getenv("TELNYX_API_KEY", "")
    telnyx_enable_transcription: bool = _as_bool(os.getenv("TELNYX_ENABLE_TRANSCRIPTION", "true"), default=True)
    telnyx_transcription_tracks: str = os.getenv("TELNYX_TRANSCRIPTION_TRACKS", "inbound")
    telnyx_speak_fallback_voice: str = os.getenv("TELNYX_SPEAK_FALLBACK_VOICE", "female")

    deepgram_api_key: str = os.getenv("DEEPGRAM_API_KEY", "")
    deepgram_model: str = os.getenv("DEEPGRAM_MODEL", "nova-3")
    deepgram_language: str = os.getenv("DEEPGRAM_LANGUAGE", "el")

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    openai_transcribe_model: str = os.getenv("OPENAI_TRANSCRIBE_MODEL", "whisper-1")
    openai_request_timeout_seconds: float = _as_float(
        os.getenv("OPENAI_REQUEST_TIMEOUT_SECONDS", "20"),
        default=20.0,
    )
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")
    azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_openai_deployment: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
    azure_openai_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
    azure_openai_transcribe_deployment: str = os.getenv("AZURE_OPENAI_TRANSCRIBE_DEPLOYMENT", "")

    cartesia_api_key: str = os.getenv("CARTESIA_API_KEY", "")
    cartesia_voice_id: str = os.getenv("CARTESIA_VOICE_ID", "")
    cartesia_model_id: str = os.getenv("CARTESIA_MODEL_ID", "sonic-2")

    tts_backend: str = os.getenv("TTS_BACKEND", "google")
    tts_output_dir: str = os.getenv("TTS_OUTPUT_DIR", "/tmp/thalpo_audio")
    google_tts_language_code: str = os.getenv("GOOGLE_TTS_LANGUAGE_CODE", "el-GR")
    google_tts_voice_name: str = os.getenv(
        "GOOGLE_TTS_VOICE_NAME",
        "el-GR-Chirp3-HD-Leda",
    )
    google_credentials_json: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON", "")
    google_tts_speaking_rate: float = _as_float(
        os.getenv("GOOGLE_TTS_SPEAKING_RATE", "0.95"),
        default=0.95,
    )

    pstn_language: str = os.getenv("PSTN_LANGUAGE", "el-GR")
    pstn_greeting_text: str = os.getenv(
        "PSTN_GREETING_TEXT",
        "Γεια σας! Είμαι η Λήδα. Χαίρομαι που σας ακούω. Πώς αισθάνεστε σήμερα;",
    )

    analysis_engine_url: str = os.getenv("ANALYSIS_ENGINE_URL", "http://localhost:8001")
    alert_engine_url: str = os.getenv("ALERT_ENGINE_URL", "http://localhost:8002")
    family_api_url: str = os.getenv("FAMILY_API_URL", "http://localhost:8003")
    internal_service_token: str = os.getenv("INTERNAL_SERVICE_TOKEN", "thalpo-internal-dev")

    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_stream_turns: str = os.getenv("REDIS_STREAM_TURNS", "thalpo.turns")

    analysis_async_enabled: bool = _as_bool(
        os.getenv("ANALYSIS_ASYNC_ENABLED", "true"),
        default=True,
    )
    request_timeout_seconds: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "3.0"))


settings = Settings()
