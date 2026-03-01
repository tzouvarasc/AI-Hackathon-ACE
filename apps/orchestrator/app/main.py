from __future__ import annotations

from pathlib import Path
import time

import httpx
from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

from apps.orchestrator.app.config import settings
from apps.orchestrator.app.mac_voice_chat_page import build_mac_voice_chat_html
from apps.orchestrator.app.pipeline import OrchestratorPipeline
from apps.orchestrator.app.sip_bridge import SIPBridge
from apps.orchestrator.app.telnyx_voice import TelnyxVoiceBridge
from shared.contracts.schemas import (
    LiveKitSipCallRequest,
    LiveKitSipCallResponse,
    LiveKitSipDispatchRequest,
    LiveKitSipDispatchResponse,
    PSTNStartRequest,
    PSTNTurnRequest,
    PSTNTurnResponse,
    ProcessTurnRequest,
    ProcessTurnResponse,
    SessionStartRequest,
    SessionStartResponse,
    SessionTokenRequest,
    SessionTokenResponse,
)

app = FastAPI(title="Thalpo Orchestrator", version="0.6.0")
pipeline = OrchestratorPipeline(settings=settings)
sip_bridge = SIPBridge(settings=settings, pipeline=pipeline)
telnyx_bridge = TelnyxVoiceBridge(settings=settings, pipeline=pipeline)


def _azure_stt_available() -> bool:
    return bool(
        settings.azure_openai_api_key
        and settings.azure_openai_endpoint
        and settings.azure_openai_transcribe_deployment
    )


class MacGreetingRequest(BaseModel):
    session_id: str
    text: str = "Γεια σας! Είμαι η Θάλπω. Θα σας παίρνω τηλέφωνο κάθε μέρα για να τα λέμε λίγο. Πώς σας λένε;"


@app.on_event("startup")
async def on_startup() -> None:
    print(
        "[orchestrator] llm_config "
        f"provider={settings.llm_provider} "
        f"openai_model={settings.openai_model} "
        f"azure_deployment={settings.azure_openai_deployment or '-'} "
        f"azure_endpoint_set={bool(settings.azure_openai_endpoint)} "
        f"openai_key_set={bool(settings.openai_api_key)} "
        f"azure_key_set={bool(settings.azure_openai_api_key)}"
    )


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await pipeline.close()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "orchestrator"}


@app.get("/v1/mac/voice-chat", response_class=HTMLResponse)
async def mac_voice_chat() -> HTMLResponse:
    # Prefer explicit Azure STT wiring; avoid enabling server STT by accident from stale OPENAI key.
    server_stt_enabled = _azure_stt_available()
    return HTMLResponse(content=build_mac_voice_chat_html(server_stt_enabled=server_stt_enabled))


@app.post("/v1/mac/transcribe")
async def mac_transcribe(
    file: UploadFile = File(...),
    language: str = Form("el"),
) -> dict[str, str | int]:
    started = time.perf_counter()
    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file")

    files = {
        "file": (
            file.filename or "audio.webm",
            audio_bytes,
            file.content_type or "application/octet-stream",
        )
    }
    provider = "none"
    payload: dict[str, str] = {}

    try:
        async with httpx.AsyncClient(timeout=max(settings.request_timeout_seconds, 30.0)) as client:
            if _azure_stt_available():
                provider = "azure"
                azure_endpoint = settings.azure_openai_endpoint.rstrip("/")
                azure_url = (
                    f"{azure_endpoint}/openai/deployments/{settings.azure_openai_transcribe_deployment}"
                    f"/audio/transcriptions?api-version={settings.azure_openai_api_version}"
                )
                response = await client.post(
                    azure_url,
                    data={"language": language},
                    files=files,
                    headers={"api-key": settings.azure_openai_api_key},
                )
                response.raise_for_status()
                payload = response.json()
            elif settings.openai_api_key:
                provider = "openai"
                response = await client.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    data={
                        "model": settings.openai_transcribe_model,
                        "language": language,
                    },
                    files=files,
                    headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                )
                response.raise_for_status()
                payload = response.json()
            else:
                raise HTTPException(
                    status_code=500,
                    detail=(
                        "No server STT configured. Set OPENAI_API_KEY or "
                        "AZURE_OPENAI_API_KEY + AZURE_OPENAI_ENDPOINT + AZURE_OPENAI_TRANSCRIBE_DEPLOYMENT."
                    ),
                )
    except HTTPException:
        raise
    except httpx.HTTPStatusError as exc:  # pragma: no cover - integration path
        status_code = exc.response.status_code
        if status_code in {401, 403}:
            raise HTTPException(
                status_code=status_code,
                detail=f"{provider.upper()} transcription auth failed (check keys/permissions)",
            ) from exc
        if status_code == 404 and provider == "azure":
            raise HTTPException(
                status_code=404,
                detail=(
                    "Azure transcription deployment not found. "
                    "Set AZURE_OPENAI_TRANSCRIBE_DEPLOYMENT to a deployed transcribe model."
                ),
            ) from exc
        if status_code == 429:
            raise HTTPException(
                status_code=429,
                detail=f"{provider.upper()} transcription quota/rate limit reached",
            ) from exc
        raise HTTPException(
            status_code=502,
            detail=f"Transcription request failed: HTTP {status_code}",
        ) from exc
    except Exception as exc:  # pragma: no cover - integration path
        raise HTTPException(status_code=502, detail=f"Transcription request failed: {exc}") from exc

    transcript = str(payload.get("text") or "").strip()
    latency_ms = int((time.perf_counter() - started) * 1000)
    return {
        "transcript": transcript,
        "provider": provider,
        "latency_ms": latency_ms,
    }


@app.post("/v1/mac/opening-greeting")
async def mac_opening_greeting(request: MacGreetingRequest) -> dict[str, str | int]:
    audio_chunk_ref, latency_ms = await pipeline.tts.synthesize(request.text, request.session_id)
    return {
        "audio_chunk_ref": audio_chunk_ref,
        "latency_ms": latency_ms,
    }


@app.get("/v1/audio/{filename}")
async def get_audio(filename: str) -> FileResponse:
    audio_root = Path(settings.tts_output_dir).resolve()
    candidate = (audio_root / filename).resolve()

    if not str(candidate).startswith(str(audio_root)):
        raise HTTPException(status_code=400, detail="Invalid audio file path")
    if not candidate.is_file():
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(path=candidate, media_type="audio/mpeg")


@app.post("/v1/sessions/start", response_model=SessionStartResponse)
async def start_session(request: SessionStartRequest) -> SessionStartResponse:
    return await pipeline.start_session(request)


@app.post("/v1/sessions/token", response_model=SessionTokenResponse)
async def create_session_token(request: SessionTokenRequest) -> SessionTokenResponse:
    try:
        return await pipeline.create_session_token(request)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/v1/turns/process", response_model=ProcessTurnResponse)
async def process_turn(
    request: ProcessTurnRequest,
    background_tasks: BackgroundTasks,
) -> ProcessTurnResponse:
    return await pipeline.process_turn(request=request, background_tasks=background_tasks)


@app.post("/v1/pstn/start", response_model=PSTNTurnResponse)
async def pstn_start(request: PSTNStartRequest) -> PSTNTurnResponse:
    return await sip_bridge.start_call(request)


@app.post("/v1/pstn/turn", response_model=PSTNTurnResponse)
async def pstn_turn(
    request: PSTNTurnRequest,
    background_tasks: BackgroundTasks,
) -> PSTNTurnResponse:
    return await sip_bridge.process_turn(request=request, background_tasks=background_tasks)


@app.post("/v1/telnyx/webhook")
async def telnyx_webhook(request: Request, background_tasks: BackgroundTasks) -> dict[str, str]:
    payload = await request.json()
    return await telnyx_bridge.handle_event(payload=payload, background_tasks=background_tasks)


@app.post("/v1/livekit/sip/dispatch", response_model=LiveKitSipDispatchResponse)
async def create_livekit_sip_dispatch(
    request: LiveKitSipDispatchRequest,
) -> LiveKitSipDispatchResponse:
    try:
        return await pipeline.create_sip_dispatch_rule(request)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/v1/livekit/sip/call", response_model=LiveKitSipCallResponse)
async def create_livekit_sip_call(request: LiveKitSipCallRequest) -> LiveKitSipCallResponse:
    try:
        return await pipeline.create_sip_participant(request)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
