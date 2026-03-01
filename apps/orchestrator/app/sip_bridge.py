from __future__ import annotations

import re
from pathlib import Path

from fastapi import BackgroundTasks

from apps.orchestrator.app.config import Settings
from apps.orchestrator.app.pipeline import OrchestratorPipeline
from shared.contracts.schemas import (
    PSTNStartRequest,
    PSTNTurnRequest,
    PSTNTurnResponse,
    ProcessTurnRequest,
)


class SIPBridge:
    """Provider-neutral PSTN turn bridge for Telnyx + LiveKit SIP integrations."""

    def __init__(self, settings: Settings, pipeline: OrchestratorPipeline) -> None:
        self.settings = settings
        self.pipeline = pipeline

    async def start_call(self, request: PSTNStartRequest) -> PSTNTurnResponse:
        user_id = self._user_id_from_phone(request.from_number)
        locale = request.locale or self.settings.pstn_language

        self.pipeline.ensure_session(
            session_id=request.call_id,
            user_id=user_id,
            channel="pstn",
            locale=locale,
        )

        greeting_text = self.settings.pstn_greeting_text
        audio_ref, _ = await self.pipeline.tts.synthesize(greeting_text, request.call_id)
        return self._build_response(
            session_id=request.call_id,
            user_id=user_id,
            assistant_text=greeting_text,
            audio_chunk_ref=audio_ref,
        )

    async def process_turn(
        self,
        request: PSTNTurnRequest,
        background_tasks: BackgroundTasks,
    ) -> PSTNTurnResponse:
        user_id = self._user_id_from_phone(request.from_number)
        locale = request.locale or self.settings.pstn_language

        self.pipeline.ensure_session(
            session_id=request.call_id,
            user_id=user_id,
            channel="pstn",
            locale=locale,
        )

        speech_text = request.speech_text.strip()
        if not speech_text:
            retry_text = "Δεν σας άκουσα καλά. Μπορείτε να το πείτε άλλη μία φορά;"
            audio_ref, _ = await self.pipeline.tts.synthesize(retry_text, request.call_id)
            return self._build_response(
                session_id=request.call_id,
                user_id=user_id,
                assistant_text=retry_text,
                audio_chunk_ref=audio_ref,
            )

        turn = await self.pipeline.process_turn(
            request=ProcessTurnRequest(
                session_id=request.call_id,
                user_id=user_id,
                raw_text=speech_text,
            ),
            background_tasks=background_tasks,
        )

        return self._build_response(
            session_id=request.call_id,
            user_id=user_id,
            assistant_text=turn.assistant_text,
            audio_chunk_ref=turn.audio_chunk_ref,
        )

    def _build_response(
        self,
        session_id: str,
        user_id: str,
        assistant_text: str,
        audio_chunk_ref: str,
    ) -> PSTNTurnResponse:
        return PSTNTurnResponse(
            session_id=session_id,
            user_id=user_id,
            assistant_text=assistant_text,
            audio_chunk_ref=audio_chunk_ref,
            audio_url=self._public_audio_url(audio_chunk_ref),
            continue_listening=True,
        )

    def _public_audio_url(self, audio_ref: str) -> str | None:
        if not audio_ref.startswith("file://"):
            return None

        filename = Path(audio_ref.replace("file://", "")).name
        if not filename:
            return None

        base = self.settings.public_base_url.rstrip("/")
        return f"{base}/v1/audio/{filename}"

    @staticmethod
    def _user_id_from_phone(phone_number: str) -> str:
        normalized = re.sub(r"[^0-9+]", "", phone_number).strip()
        if not normalized:
            return "pstn-unknown"
        return f"pstn-{normalized}"
