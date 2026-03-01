from __future__ import annotations

from fastapi import FastAPI

from apps.analysis_engine.app.config import settings
from apps.analysis_engine.app.service import AnalysisService
from shared.contracts.schemas import AnalysisRequest, AnalysisResult

app = FastAPI(title="Thalpo Analysis Engine", version="0.2.0")
service = AnalysisService(settings=settings)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "analysis_engine"}


@app.post("/v1/analyze", response_model=AnalysisResult)
async def analyze(request: AnalysisRequest) -> AnalysisResult:
    return await service.analyze(request)
