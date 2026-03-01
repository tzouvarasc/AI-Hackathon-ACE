from __future__ import annotations

import time
from uuid import uuid4

import httpx
from fastapi import BackgroundTasks

from apps.orchestrator.app.config import Settings
from apps.orchestrator.app.event_bus import TurnEventBus
from apps.orchestrator.app.providers.livekit import LiveKitProvider
from apps.orchestrator.app.providers.llm import LLMProvider
from apps.orchestrator.app.providers.stt import STTProvider
from apps.orchestrator.app.providers.tts import TTSProvider
from apps.orchestrator.app.providers.vad import VADProvider
from shared.contracts.schemas import (
    AlertDecision,
    AlertEvaluationRequest,
    AnalysisRequest,
    AnalysisResult,
    DashboardIngestRequest,
    LiveKitSipCallRequest,
    LiveKitSipCallResponse,
    LiveKitSipDispatchRequest,
    LiveKitSipDispatchResponse,
    ProcessTurnRequest,
    ProcessTurnResponse,
    SessionStartRequest,
    SessionStartResponse,
    SessionTokenRequest,
    SessionTokenResponse,
    VoiceTurnEvent,
)


class OrchestratorPipeline:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.vad = VADProvider()
        self.stt = STTProvider(
            api_key=settings.deepgram_api_key,
            model=settings.deepgram_model,
            language=settings.deepgram_language,
            timeout_seconds=settings.request_timeout_seconds,
        )
        self.llm = LLMProvider(
            provider=settings.llm_provider,
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            timeout_seconds=settings.openai_request_timeout_seconds,
            azure_api_key=settings.azure_openai_api_key,
            azure_endpoint=settings.azure_openai_endpoint,
            azure_deployment=settings.azure_openai_deployment,
            azure_api_version=settings.azure_openai_api_version,
        )
        self.tts = TTSProvider(
            backend=settings.tts_backend,
            output_dir=settings.tts_output_dir,
            timeout_seconds=settings.request_timeout_seconds,
            cartesia_api_key=settings.cartesia_api_key,
            cartesia_voice_id=settings.cartesia_voice_id,
            cartesia_model_id=settings.cartesia_model_id,
            google_language_code=settings.google_tts_language_code,
            google_voice_name=settings.google_tts_voice_name,
            google_credentials_json=settings.google_credentials_json,
            google_speaking_rate=settings.google_tts_speaking_rate,
        )
        self.livekit = LiveKitProvider(
            api_key=settings.livekit_api_key,
            api_secret=settings.livekit_api_secret,
            ws_url=settings.livekit_ws_url,
        )
        self.event_bus = TurnEventBus(
            redis_url=settings.redis_url,
            stream_name=settings.redis_stream_turns,
        )
        self.sessions: dict[str, dict[str, str]] = {}

    def ensure_session(
        self,
        session_id: str,
        user_id: str,
        channel: str = "pstn",
        locale: str = "el-GR",
    ) -> None:
        if session_id in self.sessions:
            return
        self.sessions[session_id] = {
            "user_id": user_id,
            "channel": channel,
            "locale": locale,
        }

    async def start_session(self, request: SessionStartRequest) -> SessionStartResponse:
        session_id = uuid4().hex
        self.sessions[session_id] = {
            "user_id": request.user_id,
            "channel": request.channel.value,
            "locale": request.locale,
        }
        return SessionStartResponse(session_id=session_id)

    async def create_session_token(
        self,
        request: SessionTokenRequest,
    ) -> SessionTokenResponse:
        room_name = request.room_name or f"thalpo-{request.user_id}"
        token = self.livekit.create_participant_token(
            identity=request.user_id,
            room_name=room_name,
            ttl_seconds=3600,
        )
        return SessionTokenResponse(room_name=room_name, ws_url=self.settings.livekit_ws_url, token=token)

    async def create_sip_dispatch_rule(
        self,
        request: LiveKitSipDispatchRequest,
    ) -> LiveKitSipDispatchResponse:
        inbound_trunk_id = request.inbound_trunk_id or self.settings.livekit_sip_inbound_trunk_id
        if not inbound_trunk_id:
            raise RuntimeError(
                "Missing inbound trunk id. Set LIVEKIT_SIP_INBOUND_TRUNK_ID or pass inbound_trunk_id."
            )

        room_prefix = request.room_prefix or self.settings.livekit_sip_room_prefix
        metadata = (
            request.metadata
            if request.metadata is not None
            else self.settings.livekit_sip_dispatch_metadata
        )

        dispatch_rule_id = await self.livekit.create_sip_dispatch_rule(
            inbound_trunk_id=inbound_trunk_id,
            room_prefix=room_prefix,
            metadata=metadata,
            timeout_seconds=self.settings.request_timeout_seconds,
        )
        return LiveKitSipDispatchResponse(
            dispatch_rule_id=dispatch_rule_id,
            inbound_trunk_id=inbound_trunk_id,
            room_prefix=room_prefix,
        )

    async def create_sip_participant(
        self,
        request: LiveKitSipCallRequest,
    ) -> LiveKitSipCallResponse:
        sip_trunk_id = request.sip_trunk_id or self.settings.livekit_sip_outbound_trunk_id
        if not sip_trunk_id:
            raise RuntimeError(
                "Missing outbound trunk id. Set LIVEKIT_SIP_OUTBOUND_TRUNK_ID or pass sip_trunk_id."
            )

        participant_identity = request.participant_identity or f"pstn-{request.to_number}"
        participant_name = request.participant_name or participant_identity

        sip_call_id, resolved_identity = await self.livekit.create_sip_participant(
            sip_trunk_id=sip_trunk_id,
            to_number=request.to_number,
            room_name=request.room_name,
            participant_identity=participant_identity,
            participant_name=participant_name,
            timeout_seconds=self.settings.request_timeout_seconds,
        )
        return LiveKitSipCallResponse(
            sip_call_id=sip_call_id,
            participant_identity=resolved_identity,
            room_name=request.room_name,
        )

    async def process_turn(
        self,
        request: ProcessTurnRequest,
        background_tasks: BackgroundTasks,
    ) -> ProcessTurnResponse:
        start = time.perf_counter()

        self.ensure_session(
            session_id=request.session_id,
            user_id=request.user_id,
            channel="pstn",
            locale="el-GR",
        )
        session_info = self.sessions[request.session_id]

        voice_probe = request.raw_text or ("audio_input" if request.audio_url else "")
        has_voice, vad_ms = self.vad.detect(voice_probe)

        if not has_voice:
            assistant_text = "I did not catch that. Please repeat slowly."
            audio_chunk_ref, tts_ms = await self.tts.synthesize(assistant_text, request.session_id)
            total_ms = int((time.perf_counter() - start) * 1000)
            return ProcessTurnResponse(
                session_id=request.session_id,
                transcript="",
                assistant_text=assistant_text,
                audio_chunk_ref=audio_chunk_ref,
                latency_ms={
                    "vad": vad_ms,
                    "stt": 0,
                    "llm": 0,
                    "tts": tts_ms,
                    "total": total_ms,
                },
            )

        transcript, stt_ms = await self.stt.transcribe(
            raw_text=request.raw_text,
            audio_url=request.audio_url,
        )
        locale = session_info.get("locale", "el-GR")
        assistant_text, llm_ms = await self.llm.generate_reply(transcript, locale=locale)
        audio_chunk_ref, tts_ms = await self.tts.synthesize(assistant_text, request.session_id)

        turn_event = VoiceTurnEvent(
            session_id=request.session_id,
            user_id=request.user_id,
            transcript=transcript,
            assistant_text=assistant_text,
            audio_chunk_ref=audio_chunk_ref,
        )
        background_tasks.add_task(self.event_bus.publish_turn_event, turn_event)

        if self.settings.analysis_async_enabled:
            background_tasks.add_task(
                self.run_parallel_analysis,
                session_id=request.session_id,
                user_id=request.user_id,
                transcript=transcript,
                assistant_text=assistant_text,
                audio_url=request.audio_url,
                audio_features=request.audio_features,
            )

        total_ms = int((time.perf_counter() - start) * 1000)
        return ProcessTurnResponse(
            session_id=request.session_id,
            transcript=transcript,
            assistant_text=assistant_text,
            audio_chunk_ref=audio_chunk_ref,
            latency_ms={
                "vad": vad_ms,
                "stt": stt_ms,
                "llm": llm_ms,
                "tts": tts_ms,
                "total": total_ms,
            },
        )

    async def run_parallel_analysis(
        self,
        session_id: str,
        user_id: str,
        transcript: str,
        assistant_text: str,
        audio_url: str | None,
        audio_features: dict[str, float],
    ) -> None:
        analysis_request = AnalysisRequest(
            session_id=session_id,
            user_id=user_id,
            transcript=transcript,
            audio_url=audio_url,
            audio_features=audio_features,
        )

        analysis_body = await self._post_json(
            f"{self.settings.analysis_engine_url}/v1/analyze",
            analysis_request.model_dump(mode="json"),
        )
        if analysis_body is None:
            return

        analysis_result = AnalysisResult(**analysis_body)

        alert_request = AlertEvaluationRequest(
            session_id=session_id,
            user_id=user_id,
            transcript=transcript,
            analysis=analysis_result,
        )
        alert_body = await self._post_json(
            f"{self.settings.alert_engine_url}/v1/alerts/evaluate",
            alert_request.model_dump(mode="json"),
        )
        alert_result = AlertDecision(**alert_body) if alert_body else None

        ingest_request = DashboardIngestRequest(
            session_id=session_id,
            user_id=user_id,
            transcript=transcript,
            assistant_text=assistant_text,
            analysis=analysis_result,
            alert=alert_result,
        )
        await self._post_json(
            f"{self.settings.family_api_url}/v1/dashboard/{user_id}/ingest",
            ingest_request.model_dump(mode="json"),
            headers={"x-internal-token": self.settings.internal_service_token},
        )

    async def _post_json(
        self,
        url: str,
        payload: dict,
        headers: dict[str, str] | None = None,
    ) -> dict | None:
        try:
            async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
        except Exception as exc:  # pragma: no cover - integration path
            print(f"[orchestrator] failed POST {url}: {exc}")
            return None

    async def close(self) -> None:
        await self.event_bus.close()
