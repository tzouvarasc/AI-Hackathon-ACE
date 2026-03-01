from __future__ import annotations

from apps.alert_engine.app.config import Settings
from apps.alert_engine.app.decision import evaluate_alert
from apps.alert_engine.app.notifier import TelnyxNotifier
from shared.contracts.schemas import AlertDecision, AlertEvaluationRequest


class AlertService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.notifier = TelnyxNotifier(
            api_key=settings.telnyx_api_key,
            from_number=settings.telnyx_from,
            to_number=settings.telnyx_to,
            messaging_profile_id=settings.telnyx_messaging_profile_id,
            timeout_seconds=settings.request_timeout_seconds,
        )

    async def evaluate(self, request: AlertEvaluationRequest) -> AlertDecision:
        decision = evaluate_alert(request)

        if decision.notify_family and self.settings.auto_dispatch_sms and decision.sms_message:
            delivered = await self.notifier.send_sms(decision.sms_message)
            if delivered:
                decision.reasons.append("SMS dispatched")
            else:
                decision.reasons.append("SMS dispatch failed")

        return decision
