from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Channel(str, Enum):
    pstn = "pstn"
    webrtc = "webrtc"


class AlertSeverity(str, Enum):
    none = "none"
    warning = "warning"
    critical = "critical"


class UserRole(str, Enum):
    admin = "admin"
    caregiver = "caregiver"
    clinician = "clinician"
    service = "service"


class SessionStartRequest(BaseModel):
    user_id: str
    channel: Channel = Channel.pstn
    locale: str = "el-GR"


class SessionStartResponse(BaseModel):
    session_id: str
    started_at: str = Field(default_factory=utc_now_iso)


class SessionTokenRequest(BaseModel):
    user_id: str
    room_name: str | None = None


class SessionTokenResponse(BaseModel):
    room_name: str
    ws_url: str
    token: str
    expires_in_seconds: int = 3600


class ProcessTurnRequest(BaseModel):
    session_id: str
    user_id: str
    raw_text: str = ""
    audio_url: str | None = None
    audio_features: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_input(self) -> "ProcessTurnRequest":
        if not self.raw_text.strip() and not self.audio_url:
            raise ValueError("Provide raw_text or audio_url")
        return self


class PSTNStartRequest(BaseModel):
    call_id: str
    from_number: str
    to_number: str | None = None
    locale: str = "el-GR"


class PSTNTurnRequest(BaseModel):
    call_id: str
    from_number: str
    speech_text: str = ""
    locale: str = "el-GR"


class PSTNTurnResponse(BaseModel):
    session_id: str
    user_id: str
    assistant_text: str
    audio_chunk_ref: str
    audio_url: str | None = None
    continue_listening: bool = True


class LiveKitSipDispatchRequest(BaseModel):
    inbound_trunk_id: str | None = None
    room_prefix: str | None = None
    metadata: str | None = None


class LiveKitSipDispatchResponse(BaseModel):
    dispatch_rule_id: str
    inbound_trunk_id: str
    room_prefix: str


class LiveKitSipCallRequest(BaseModel):
    sip_trunk_id: str | None = None
    to_number: str
    room_name: str
    participant_identity: str | None = None
    participant_name: str | None = None


class LiveKitSipCallResponse(BaseModel):
    sip_call_id: str
    participant_identity: str
    room_name: str


class AnalysisRequest(BaseModel):
    session_id: str
    user_id: str
    transcript: str
    audio_url: str | None = None
    audio_features: dict[str, float] = Field(default_factory=dict)


class AnalysisResult(BaseModel):
    emotion_label: str = "neutral"
    emotion_score: float = 0.0
    cognitive_score: float = 1.0
    risk_flags: list[str] = Field(default_factory=list)
    biomarkers: dict[str, float] = Field(default_factory=dict)
    created_at: str = Field(default_factory=utc_now_iso)


class AlertEvaluationRequest(BaseModel):
    session_id: str
    user_id: str
    transcript: str
    analysis: AnalysisResult


class AlertDecision(BaseModel):
    severity: AlertSeverity = AlertSeverity.none
    notify_family: bool = False
    reasons: list[str] = Field(default_factory=list)
    sms_message: str | None = None
    created_at: str = Field(default_factory=utc_now_iso)


class DashboardIngestRequest(BaseModel):
    session_id: str
    user_id: str
    transcript: str
    assistant_text: str | None = None
    analysis: AnalysisResult
    alert: AlertDecision | None = None


class DashboardSnapshot(BaseModel):
    user_id: str
    last_updated: str = Field(default_factory=utc_now_iso)
    cognitive_score: float | None = None
    emotion_score: float | None = None
    emotion_label: str | None = None
    recent_flags: list[str] = Field(default_factory=list)
    active_alerts: list[AlertDecision] = Field(default_factory=list)
    cards: dict[str, Any] = Field(default_factory=dict)


class DashboardInsights(BaseModel):
    user_id: str
    window_days: int
    total_turns: int = 0
    sessions_count: int = 0
    avg_emotion_score: float | None = None
    avg_cognitive_score: float | None = None
    risk_flag_counts: dict[str, int] = Field(default_factory=dict)
    alert_counts: dict[str, int] = Field(default_factory=dict)
    top_keywords: list[str] = Field(default_factory=list)
    suggested_actions: list[str] = Field(default_factory=list)
    summary: str = ""
    generated_at: str = Field(default_factory=utc_now_iso)


class ProcessTurnResponse(BaseModel):
    session_id: str
    transcript: str
    assistant_text: str
    audio_chunk_ref: str
    latency_ms: dict[str, int]


class VoiceTurnEvent(BaseModel):
    session_id: str
    user_id: str
    transcript: str
    assistant_text: str
    audio_chunk_ref: str
    created_at: str = Field(default_factory=utc_now_iso)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    role: UserRole
    user_id: str


class UserCreateRequest(BaseModel):
    username: str
    password: str
    display_name: str | None = None
    role: UserRole = UserRole.caregiver


class UserView(BaseModel):
    user_id: str
    username: str
    display_name: str
    role: UserRole
    is_active: bool
    created_at: str
