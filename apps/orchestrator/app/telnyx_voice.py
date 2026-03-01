from __future__ import annotations

import hashlib
import re
from collections import deque
from pathlib import Path
from typing import Any

import httpx
from fastapi import BackgroundTasks

from apps.orchestrator.app.config import Settings
from apps.orchestrator.app.pipeline import OrchestratorPipeline
from shared.contracts.schemas import ProcessTurnRequest


class TelnyxVoiceBridge:
    """Handles Telnyx Voice API webhooks and maps them to the Thalpo turn pipeline."""

    def __init__(self, settings: Settings, pipeline: OrchestratorPipeline) -> None:
        self.settings = settings
        self.pipeline = pipeline
        self._recent_event_ids: deque[str] = deque(maxlen=2000)
        self._recent_event_index: set[str] = set()
        self._call_state: dict[str, dict[str, str | bool]] = {}

    async def handle_event(
        self,
        payload: dict[str, Any],
        background_tasks: BackgroundTasks,
    ) -> dict[str, str]:
        data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
        event_type = self._as_str(data.get("event_type") or payload.get("event_type"))
        if not event_type:
            return {"status": "ignored", "reason": "missing_event_type"}

        event_id = self._as_str(data.get("id") or payload.get("id"))
        if self._is_duplicate_event(event_id):
            return {"status": "duplicate"}

        event_payload = data.get("payload") if isinstance(data.get("payload"), dict) else {}
        call_control_id = self._as_str(event_payload.get("call_control_id"))
        call_session_id = self._as_str(event_payload.get("call_session_id")) or call_control_id
        if not call_control_id or not call_session_id:
            return {"status": "ignored", "reason": "missing_call_identifiers"}

        from_number = self._extract_phone_number(event_payload.get("from"))
        to_number = self._extract_phone_number(event_payload.get("to"))

        state = self._call_state.setdefault(call_session_id, {})
        state["call_control_id"] = call_control_id
        state.setdefault("from_number", from_number or "unknown")
        state.setdefault("to_number", to_number or "")

        if event_type == "call.initiated":
            await self._answer_call(call_control_id=call_control_id, call_session_id=call_session_id)
            return {"status": "ok", "event": event_type}

        if event_type == "call.answered":
            await self._on_call_answered(
                call_control_id=call_control_id,
                call_session_id=call_session_id,
                from_number=from_number,
                to_number=to_number,
            )
            return {"status": "ok", "event": event_type}

        if event_type == "call.transcription":
            transcript, is_final = self._extract_transcript(event_payload)
            if is_final and transcript:
                await self._on_transcription_turn(
                    call_control_id=call_control_id,
                    call_session_id=call_session_id,
                    transcript=transcript,
                    background_tasks=background_tasks,
                )
            return {"status": "ok", "event": event_type}

        if event_type in {"call.hangup", "call.ended"}:
            self._call_state.pop(call_session_id, None)
            return {"status": "ok", "event": event_type}

        return {"status": "ignored", "event": event_type}

    async def _on_call_answered(
        self,
        call_control_id: str,
        call_session_id: str,
        from_number: str,
        to_number: str,
    ) -> None:
        state = self._call_state.setdefault(call_session_id, {})
        if from_number:
            state["from_number"] = from_number
        if to_number:
            state["to_number"] = to_number

        user_id = self._user_id_from_phone(self._as_str(state.get("from_number") or from_number))
        self.pipeline.ensure_session(
            session_id=call_session_id,
            user_id=user_id,
            channel="pstn",
            locale=self.settings.pstn_language,
        )

        if not bool(state.get("greeted")):
            greeting_text = self.settings.pstn_greeting_text
            audio_ref, _ = await self.pipeline.tts.synthesize(greeting_text, call_session_id)
            audio_url = self._public_audio_url(audio_ref)
            if audio_url:
                await self._play_audio(call_control_id, call_session_id, audio_url, "greeting")
            else:
                await self._speak_text(call_control_id, call_session_id, greeting_text, "greeting")
            state["greeted"] = True

        if self.settings.telnyx_enable_transcription and not bool(state.get("transcription_started")):
            await self._start_transcription(call_control_id, call_session_id)
            state["transcription_started"] = True

    async def _on_transcription_turn(
        self,
        call_control_id: str,
        call_session_id: str,
        transcript: str,
        background_tasks: BackgroundTasks,
    ) -> None:
        state = self._call_state.setdefault(call_session_id, {})
        from_number = self._as_str(state.get("from_number") or "unknown")
        user_id = self._user_id_from_phone(from_number)

        turn = await self.pipeline.process_turn(
            request=ProcessTurnRequest(
                session_id=call_session_id,
                user_id=user_id,
                raw_text=transcript,
            ),
            background_tasks=background_tasks,
        )

        audio_url = self._public_audio_url(turn.audio_chunk_ref)
        if audio_url:
            await self._play_audio(call_control_id, call_session_id, audio_url, "turn")
        else:
            await self._speak_text(call_control_id, call_session_id, turn.assistant_text, "turn")

    async def _answer_call(self, call_control_id: str, call_session_id: str) -> bool:
        return await self._post_call_action(
            call_control_id=call_control_id,
            call_session_id=call_session_id,
            action="answer",
            payload={},
            salt="answer",
        )

    async def _start_transcription(self, call_control_id: str, call_session_id: str) -> bool:
        return await self._post_call_action(
            call_control_id=call_control_id,
            call_session_id=call_session_id,
            action="transcription_start",
            payload={"transcription_tracks": self.settings.telnyx_transcription_tracks},
            salt="transcription-start",
        )

    async def _play_audio(
        self,
        call_control_id: str,
        call_session_id: str,
        audio_url: str,
        salt: str,
    ) -> bool:
        return await self._post_call_action(
            call_control_id=call_control_id,
            call_session_id=call_session_id,
            action="playback_start",
            payload={"audio_url": audio_url},
            salt=f"playback-{salt}-{audio_url}",
        )

    async def _speak_text(
        self,
        call_control_id: str,
        call_session_id: str,
        text: str,
        salt: str,
    ) -> bool:
        return await self._post_call_action(
            call_control_id=call_control_id,
            call_session_id=call_session_id,
            action="speak",
            payload={
                "payload": text,
                "voice": self.settings.telnyx_speak_fallback_voice,
                "language": self.settings.pstn_language,
            },
            salt=f"speak-{salt}-{text}",
        )

    async def _post_call_action(
        self,
        call_control_id: str,
        call_session_id: str,
        action: str,
        payload: dict[str, Any],
        salt: str,
    ) -> bool:
        if not self.settings.telnyx_api_key:
            print("[telnyx] TELNYX_API_KEY is missing")
            return False

        url = f"https://api.telnyx.com/v2/calls/{call_control_id}/actions/{action}"
        body = dict(payload)
        body["command_id"] = self._command_id(action=action, call_session_id=call_session_id, salt=salt)

        headers = {
            "Authorization": f"Bearer {self.settings.telnyx_api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
                response = await client.post(url, json=body, headers=headers)
                response.raise_for_status()
            return True
        except Exception as exc:  # pragma: no cover - external API path
            print(f"[telnyx] action={action} failed: {exc}")
            return False

    def _public_audio_url(self, audio_ref: str) -> str | None:
        if not audio_ref.startswith("file://"):
            return None

        filename = Path(audio_ref.replace("file://", "")).name
        if not filename:
            return None

        base = self.settings.public_base_url.rstrip("/")
        return f"{base}/v1/audio/{filename}"

    @staticmethod
    def _extract_phone_number(value: Any) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            for key in ("phone_number", "number", "e164", "value"):
                candidate = value.get(key)
                if isinstance(candidate, str) and candidate.strip():
                    return candidate
        return ""

    @staticmethod
    def _extract_transcript(payload: dict[str, Any]) -> tuple[str, bool]:
        transcription = payload.get("transcription_data")
        if not isinstance(transcription, dict):
            transcription = payload.get("transcription")

        transcript = ""
        is_final = True

        if isinstance(transcription, dict):
            transcript = str(transcription.get("transcript") or transcription.get("text") or "").strip()
            is_final = bool(transcription.get("is_final", True))
        else:
            transcript = str(payload.get("transcript") or payload.get("text") or "").strip()

        return transcript, is_final

    @staticmethod
    def _as_str(value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip()

    @staticmethod
    def _user_id_from_phone(phone_number: str) -> str:
        normalized = re.sub(r"[^0-9+]", "", phone_number).strip()
        if not normalized:
            return "pstn-unknown"
        return f"pstn-{normalized}"

    @staticmethod
    def _command_id(action: str, call_session_id: str, salt: str) -> str:
        digest = hashlib.sha1(f"{action}:{call_session_id}:{salt}".encode("utf-8")).hexdigest()
        return digest[:32]

    def _is_duplicate_event(self, event_id: str) -> bool:
        if not event_id:
            return False

        if event_id in self._recent_event_index:
            return True

        if len(self._recent_event_ids) == self._recent_event_ids.maxlen:
            oldest = self._recent_event_ids.popleft()
            self._recent_event_index.discard(oldest)

        self._recent_event_ids.append(event_id)
        self._recent_event_index.add(event_id)
        return False
