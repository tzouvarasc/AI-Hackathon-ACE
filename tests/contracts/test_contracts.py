import pytest

from shared.contracts.schemas import AnalysisResult, DashboardIngestRequest, DashboardInsights, ProcessTurnRequest


def test_process_turn_requires_text_or_audio_url() -> None:
    with pytest.raises(ValueError):
        ProcessTurnRequest(session_id="s1", user_id="u1", raw_text="", audio_url=None)


def test_process_turn_accepts_audio_only() -> None:
    request = ProcessTurnRequest(
        session_id="s1",
        user_id="u1",
        raw_text="",
        audio_url="https://example.com/audio.wav",
    )

    assert request.audio_url == "https://example.com/audio.wav"


def test_dashboard_ingest_accepts_optional_assistant_text() -> None:
    payload = DashboardIngestRequest(
        session_id="s1",
        user_id="u1",
        transcript="Γεια σου",
        analysis=AnalysisResult(),
    )
    assert payload.assistant_text is None

    with_reply = DashboardIngestRequest(
        session_id="s1",
        user_id="u1",
        transcript="Γεια σου",
        assistant_text="Γεια σας, πώς είστε σήμερα;",
        analysis=AnalysisResult(),
    )
    assert with_reply.assistant_text is not None


def test_dashboard_insights_defaults() -> None:
    insights = DashboardInsights(user_id="u1", window_days=30)
    assert insights.total_turns == 0
    assert insights.sessions_count == 0
