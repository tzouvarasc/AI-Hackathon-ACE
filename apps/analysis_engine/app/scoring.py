from __future__ import annotations

from shared.contracts.schemas import AnalysisResult

FEAR_KEYWORDS = {"afraid", "panic", "help", "emergency", "cannot breathe", "scared"}
SAD_KEYWORDS = {"sad", "lonely", "cry", "hopeless", "down"}
COGNITIVE_KEYWORDS = {"forgot", "confused", "lost", "where am i", "what day"}
MEDS_KEYWORDS = {"missed my medicine", "forgot my pills", "did not take meds"}
FALL_KEYWORDS = {"fell", "fall", "dizzy", "cannot stand"}


def _count_hits(text: str, keywords: set[str]) -> int:
    lowered = text.lower()
    return sum(1 for keyword in keywords if keyword in lowered)


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def score_analysis(transcript: str, audio_features: dict[str, float]) -> AnalysisResult:
    fear_hits = _count_hits(transcript, FEAR_KEYWORDS)
    sad_hits = _count_hits(transcript, SAD_KEYWORDS)
    cognitive_hits = _count_hits(transcript, COGNITIVE_KEYWORDS)
    meds_hits = _count_hits(transcript, MEDS_KEYWORDS)
    fall_hits = _count_hits(transcript, FALL_KEYWORDS)

    stress_signal = float(audio_features.get("stress", 0.0))
    disfluency_signal = float(audio_features.get("speech_disfluency", 0.0))

    emotion_score = _clamp(0.15 + (fear_hits * 0.22) + (sad_hits * 0.10) + (stress_signal * 0.30))
    if fear_hits > 0 or emotion_score >= 0.75:
        emotion_label = "fear"
    elif sad_hits > 0:
        emotion_label = "sadness"
    else:
        emotion_label = "neutral"

    cognitive_score = _clamp(
        1.0 - (cognitive_hits * 0.18) - (meds_hits * 0.12) - (disfluency_signal * 0.25)
    )

    risk_flags: list[str] = []
    lowered = transcript.lower()
    if meds_hits > 0:
        risk_flags.append("missed_meds")
    if cognitive_hits > 0:
        risk_flags.append("cognitive_decline")
    if fall_hits > 0:
        risk_flags.append("fall_risk")
    if fear_hits > 0 and ("help" in lowered or "emergency" in lowered):
        risk_flags.append("acute_distress")

    biomarkers = {
        "prosody_stress": round(_clamp(stress_signal), 3),
        "speech_disfluency": round(_clamp(disfluency_signal), 3),
        "fear_keyword_hits": float(fear_hits),
    }

    return AnalysisResult(
        emotion_label=emotion_label,
        emotion_score=round(emotion_score, 3),
        cognitive_score=round(cognitive_score, 3),
        risk_flags=risk_flags,
        biomarkers=biomarkers,
    )
