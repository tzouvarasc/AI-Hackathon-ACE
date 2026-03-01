from apps.alert_engine.app.decision import evaluate_alert
from apps.analysis_engine.app.scoring import score_analysis
from shared.contracts.schemas import AlertEvaluationRequest


def test_analysis_flags_missed_meds() -> None:
    result = score_analysis(
        transcript="I forgot my pills and feel scared",
        audio_features={"stress": 0.7, "speech_disfluency": 0.1},
    )

    assert "missed_meds" in result.risk_flags
    assert result.emotion_score > 0.5


def test_alert_goes_critical_for_distress() -> None:
    analysis = score_analysis(
        transcript="Help me, I am afraid and this is an emergency",
        audio_features={"stress": 0.9},
    )
    request = AlertEvaluationRequest(
        session_id="s1",
        user_id="u1",
        transcript="Help me, I am afraid and this is an emergency",
        analysis=analysis,
    )

    decision = evaluate_alert(request)

    assert decision.notify_family is True
    assert decision.severity.value == "critical"
