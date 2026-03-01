from __future__ import annotations

from shared.contracts.schemas import AlertDecision, AlertEvaluationRequest, AlertSeverity

CRITICAL_FLAGS = {"acute_distress", "fall_risk"}
WARNING_FLAGS = {"missed_meds", "cognitive_decline"}
EMERGENCY_KEYWORDS = {"help", "panic", "emergency", "cannot breathe", "sos"}


def evaluate_alert(request: AlertEvaluationRequest) -> AlertDecision:
    reasons: list[str] = []
    severity = AlertSeverity.none

    flags = set(request.analysis.risk_flags)
    text = request.transcript.lower()

    if request.analysis.emotion_score >= 0.8 and any(keyword in text for keyword in EMERGENCY_KEYWORDS):
        severity = AlertSeverity.critical
        reasons.append("High fear signal with emergency language")

    matched_critical_flags = sorted(flags.intersection(CRITICAL_FLAGS))
    if matched_critical_flags:
        severity = AlertSeverity.critical
        reasons.append(f"Critical risk flags: {', '.join(matched_critical_flags)}")

    if severity != AlertSeverity.critical:
        if request.analysis.cognitive_score <= 0.35:
            severity = AlertSeverity.warning
            reasons.append("Low cognitive score")

        matched_warning_flags = sorted(flags.intersection(WARNING_FLAGS))
        if matched_warning_flags:
            severity = AlertSeverity.warning
            reasons.append(f"Warning risk flags: {', '.join(matched_warning_flags)}")

    reasons = list(dict.fromkeys(reasons))
    notify_family = severity != AlertSeverity.none

    sms_message = None
    if notify_family:
        reason_summary = reasons[0] if reasons else "No reason provided"
        sms_message = (
            f"[THALPO] User {request.user_id}: {severity.value.upper()} alert. "
            f"{reason_summary}."
        )

    return AlertDecision(
        severity=severity,
        notify_family=notify_family,
        reasons=reasons,
        sms_message=sms_message,
    )
