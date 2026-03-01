from __future__ import annotations

from apps.analysis_engine.app.config import Settings
from apps.analysis_engine.app.providers.hume import HumeProvider
from apps.analysis_engine.app.providers.langaware import LangawareProvider
from apps.analysis_engine.app.scoring import score_analysis
from shared.contracts.schemas import AnalysisRequest, AnalysisResult


class AnalysisService:
    def __init__(self, settings: Settings) -> None:
        self.hume = HumeProvider(
            api_key=settings.hume_api_key,
            api_url=settings.hume_api_url,
            timeout_seconds=settings.request_timeout_seconds,
        )
        self.langaware = LangawareProvider(
            api_key=settings.langaware_api_key,
            api_url=settings.langaware_api_url,
            timeout_seconds=settings.request_timeout_seconds,
        )

    async def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        base = score_analysis(
            transcript=request.transcript,
            audio_features=request.audio_features,
        )

        hume_result = await self.hume.analyze(request.transcript, request.audio_url)
        langaware_result = await self.langaware.analyze(request.transcript, request.audio_url)

        emotion_label = base.emotion_label
        emotion_score = base.emotion_score
        cognitive_score = base.cognitive_score
        risk_flags = list(base.risk_flags)
        biomarkers = dict(base.biomarkers)

        if hume_result:
            external_label = hume_result.get("emotion_label")
            external_score = hume_result.get("emotion_score")
            if isinstance(external_label, str) and external_label:
                emotion_label = external_label
            if isinstance(external_score, (int, float)):
                emotion_score = max(0.0, min(1.0, float(external_score)))
            biomarkers["hume_connected"] = 1.0

        if langaware_result:
            external_cognitive = langaware_result.get("cognitive_score")
            external_flags = langaware_result.get("risk_flags") or []
            if isinstance(external_cognitive, (int, float)):
                cognitive_score = max(0.0, min(1.0, float(external_cognitive)))
            if isinstance(external_flags, list):
                risk_flags.extend(str(flag) for flag in external_flags)
            biomarkers["langaware_connected"] = 1.0

        merged_flags = list(dict.fromkeys(risk_flags))
        return AnalysisResult(
            emotion_label=emotion_label,
            emotion_score=round(emotion_score, 3),
            cognitive_score=round(cognitive_score, 3),
            risk_flags=merged_flags,
            biomarkers=biomarkers,
        )
