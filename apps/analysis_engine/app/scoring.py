from __future__ import annotations

from shared.contracts.schemas import AnalysisResult

# Greek entries use word stems so inflected forms are matched without a lemmatizer.
# e.g. "φοβ" matches φοβάμαι, φοβισμένος, φόβος, etc.

FEAR_KEYWORDS = {
    # English
    "afraid", "panic", "help", "emergency", "cannot breathe", "scared", "sos",
    # Greek stems
    "φοβ",       # φοβάμαι, φόβος, φοβισμένος
    "βοηθ",      # βοήθεια, βοήθησέ με
    "πανικ",     # πανικός, πανικόβλητος
    "τρομ",      # τρόμος, τρομαγμένος
    "επείγ",     # επείγον
    "ανάσ",      # δεν μπορώ να αναπνεύσω (αναπνοή)
    "δεν μπορω να αναπν",
}

SAD_KEYWORDS = {
    # English
    "sad", "lonely", "cry", "hopeless", "down",
    # Greek stems
    "μοναξ",       # μοναξιά, μόνος
    "κλάψ",        # κλαίω, κλάψε
    "κλαιω",
    "απελπ",       # απελπισία
    "λύπ",         # λύπη, λυπημένος
    "στεναχωρ",    # στεναχώρια
    "μελαγχολ",    # μελαγχολία
    "θλίψ",        # θλίψη
}

COGNITIVE_KEYWORDS = {
    # English
    "forgot", "confused", "lost", "where am i", "what day",
    # Greek stems
    "ξέχασ",      # ξέχασα
    "ξεχν",       # ξεχνώ
    "μπερδ",      # μπερδεύτηκα, μπερδεμένος
    "χαμέν",      # χαμένος
    "δεν θυμ",    # δεν θυμάμαι
    "χάθηκ",      # χάθηκα
    "δεν ξερ",    # δεν ξέρω
    "δεν καταλαβ",
}

MEDS_KEYWORDS = {
    # English
    "missed my medicine", "forgot my pills", "did not take meds",
    # Greek stems
    "φαρμακ",       # φάρμακο, φάρμακα
    "χαπι",         # χάπι
    "δόσ",          # δόση
    "ξέχασα τα φ",  # ξέχασα τα φάρμακα
}

FALL_KEYWORDS = {
    # English
    "fell", "fall", "dizzy", "cannot stand",
    # Greek stems
    "έπεσ",         # έπεσα
    "πέφτ",         # πέφτω
    "ζάλ",          # ζάλη, ζαλίζομαι
    "σκόνταψ",      # σκόνταψα
    "χτύπησ",       # χτύπησα
    "δεν μπορω να σταθ",
}


def _count_hits(text: str, keywords: set[str]) -> int:
    lowered = text.lower()
    return sum(1 for keyword in keywords if keyword in lowered)


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def score_analysis(
    transcript: str,
    audio_features: dict[str, float],
    history: list[str] | None = None,
) -> AnalysisResult:
    fear_hits = _count_hits(transcript, FEAR_KEYWORDS)
    sad_hits = _count_hits(transcript, SAD_KEYWORDS)
    cognitive_hits = _count_hits(transcript, COGNITIVE_KEYWORDS)
    meds_hits = _count_hits(transcript, MEDS_KEYWORDS)
    fall_hits = _count_hits(transcript, FALL_KEYWORDS)

    stress_signal = float(audio_features.get("stress", 0.0))
    disfluency_signal = float(audio_features.get("speech_disfluency", 0.0))

    # History reinforcement: repeated signals across recent turns increase weight.
    # Cap reinforcement at 1.5x to avoid runaway amplification.
    fear_reinforcement = 1.0
    cognitive_reinforcement = 1.0
    if history:
        history_fear_hits = sum(_count_hits(t, FEAR_KEYWORDS) for t in history[-3:])
        history_cognitive_hits = sum(_count_hits(t, COGNITIVE_KEYWORDS) for t in history[-3:])
        fear_reinforcement = min(1.5, 1.0 + history_fear_hits * 0.15)
        cognitive_reinforcement = min(1.5, 1.0 + history_cognitive_hits * 0.15)

    # No arbitrary baseline — score is 0 when no signals are present.
    emotion_score = _clamp(
        (fear_hits * 0.22 * fear_reinforcement)
        + (sad_hits * 0.10)
        + (stress_signal * 0.30)
    )

    if fear_hits > 0 or emotion_score >= 0.75:
        emotion_label = "fear"
    elif sad_hits > 0:
        emotion_label = "sadness"
    else:
        emotion_label = "neutral"

    cognitive_score = _clamp(
        1.0
        - (cognitive_hits * 0.18 * cognitive_reinforcement)
        - (meds_hits * 0.12)
        - (disfluency_signal * 0.25)
    )

    risk_flags: list[str] = []
    lowered = transcript.lower()
    if meds_hits > 0:
        risk_flags.append("missed_meds")
    if cognitive_hits > 0:
        risk_flags.append("cognitive_decline")
    if fall_hits > 0:
        risk_flags.append("fall_risk")
    if fear_hits > 0 and any(kw in lowered for kw in {"help", "emergency", "βοηθ", "επείγ", "sos"}):
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
