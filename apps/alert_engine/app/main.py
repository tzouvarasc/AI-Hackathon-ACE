from __future__ import annotations

from fastapi import FastAPI

from apps.alert_engine.app.config import settings
from apps.alert_engine.app.service import AlertService
from shared.contracts.schemas import AlertDecision, AlertEvaluationRequest

app = FastAPI(title="Thalpo Alert Engine", version="0.3.0")
service = AlertService(settings=settings)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "alert_engine"}


@app.post("/v1/alerts/evaluate", response_model=AlertDecision)
async def evaluate(request: AlertEvaluationRequest) -> AlertDecision:
    return await service.evaluate(request)
