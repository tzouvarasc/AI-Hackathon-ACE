from __future__ import annotations

import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.family_api.app.models import DashboardEvent, DashboardSnapshotModel, User
from shared.contracts.schemas import (
    AlertDecision,
    AlertSeverity,
    AnalysisResult,
    DashboardIngestRequest,
    DashboardInsights,
    DashboardSnapshot,
    UserRole,
    UserView,
)


def _parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


_STOPWORDS = {
    "και",
    "στο",
    "στη",
    "στην",
    "στον",
    "τον",
    "την",
    "των",
    "ένα",
    "μια",
    "είμαι",
    "ειμαι",
    "είναι",
    "να",
    "σε",
    "για",
    "με",
    "που",
    "πως",
    "τι",
    "το",
    "τα",
    "ο",
    "η",
    "οι",
    "i",
    "you",
    "the",
    "and",
    "to",
    "a",
    "of",
    "is",
    "it",
}


def _extract_keywords(text: str) -> list[str]:
    tokens = re.findall(r"[^\W\d_]{3,}", (text or "").lower(), flags=re.UNICODE)
    return [token for token in tokens if token not in _STOPWORDS]


def _counter_to_sorted_dict(counter: Counter[str]) -> dict[str, int]:
    items = sorted(counter.items(), key=lambda pair: (-pair[1], pair[0]))
    return {key: int(value) for key, value in items}


def _build_suggested_actions(
    avg_emotion: float | None,
    avg_cognitive: float | None,
    risk_counts: Counter[str],
    alert_counts: Counter[str],
) -> list[str]:
    actions: list[str] = []
    if alert_counts.get(AlertSeverity.critical.value, 0) > 0:
        actions.append("Άμεσο follow-up με οικογένεια λόγω κρίσιμων alerts.")
    if risk_counts.get("acute_distress", 0) > 0:
        actions.append("Ενεργοποίηση πρωτοκόλλου distress και έλεγχος ασφάλειας χρήστη.")
    if risk_counts.get("missed_meds", 0) >= 2:
        actions.append("Προσθήκη καθημερινής υπενθύμισης φαρμάκων και επιβεβαίωση λήψης.")
    if risk_counts.get("cognitive_decline", 0) >= 2 or (avg_cognitive is not None and avg_cognitive < 0.65):
        actions.append("Προτείνεται γνωστική επανεκτίμηση και εβδομαδιαίο monitoring.")
    if risk_counts.get("fall_risk", 0) > 0:
        actions.append("Έλεγχος ρίσκου πτώσης και οδηγίες πρόληψης στο σπίτι.")
    if avg_emotion is not None and avg_emotion >= 0.7:
        actions.append("Συχνότερα check-ins για συναισθηματική υποστήριξη.")
    if not actions:
        actions.append("Συνέχιση παρακολούθησης με την τρέχουσα συχνότητα.")
    return actions


def _build_summary(
    total_turns: int,
    sessions_count: int,
    avg_emotion: float | None,
    avg_cognitive: float | None,
    risk_counts: Counter[str],
    alert_counts: Counter[str],
) -> str:
    if total_turns == 0:
        return "Δεν υπάρχουν ακόμη αρκετά δεδομένα συνομιλιών για συμπεράσματα."

    parts = [
        f"Αναλύθηκαν {total_turns} turns σε {sessions_count} συνεδρίες.",
    ]
    if avg_emotion is not None:
        parts.append(f"Μέσο emotion score: {avg_emotion:.2f}.")
    if avg_cognitive is not None:
        parts.append(f"Μέσο cognitive score: {avg_cognitive:.2f}.")
    if risk_counts:
        dominant_risk, dominant_count = risk_counts.most_common(1)[0]
        parts.append(f"Συχνότερο risk flag: {dominant_risk} ({dominant_count} φορές).")
    if alert_counts.get(AlertSeverity.critical.value, 0) > 0:
        parts.append("Υπάρχουν κρίσιμα alerts στο επιλεγμένο διάστημα.")
    elif alert_counts.get(AlertSeverity.warning.value, 0) > 0:
        parts.append("Υπάρχουν προειδοποιητικά alerts που χρειάζονται παρακολούθηση.")
    else:
        parts.append("Δεν καταγράφηκαν alerts υψηλής σοβαρότητας.")
    return " ".join(parts)


class FamilyRepository:
    @staticmethod
    async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
        result = await session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(
        session: AsyncSession,
        username: str,
        password_hash: str,
        role: UserRole,
        display_name: str,
    ) -> User:
        user = User(
            user_id=f"usr_{uuid4().hex[:8]}",
            username=username,
            password_hash=password_hash,
            role=role.value,
            display_name=display_name,
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def ensure_admin_user(
        session: AsyncSession,
        username: str,
        password_hash: str,
        display_name: str,
    ) -> User:
        existing = await FamilyRepository.get_user_by_username(session, username)
        if existing:
            return existing

        return await FamilyRepository.create_user(
            session=session,
            username=username,
            password_hash=password_hash,
            role=UserRole.admin,
            display_name=display_name,
        )

    @staticmethod
    async def ingest_event(
        session: AsyncSession,
        event: DashboardIngestRequest,
    ) -> DashboardSnapshot:
        alert = event.alert
        db_event = DashboardEvent(
            session_id=event.session_id,
            user_id=event.user_id,
            transcript=event.transcript,
            assistant_text=event.assistant_text,
            emotion_label=event.analysis.emotion_label,
            emotion_score=event.analysis.emotion_score,
            cognitive_score=event.analysis.cognitive_score,
            risk_flags=list(event.analysis.risk_flags),
            biomarkers=dict(event.analysis.biomarkers),
            alert_severity=alert.severity.value if alert else None,
            alert_reasons=list(alert.reasons) if alert else [],
            alert_message=alert.sms_message if alert else None,
            created_at=_parse_datetime(event.analysis.created_at) or datetime.now(timezone.utc),
        )
        session.add(db_event)

        snapshot = await session.get(DashboardSnapshotModel, event.user_id)
        if snapshot is None:
            snapshot = DashboardSnapshotModel(user_id=event.user_id)
            session.add(snapshot)

        snapshot.last_updated = _parse_datetime(event.analysis.created_at) or snapshot.last_updated
        snapshot.cognitive_score = event.analysis.cognitive_score
        snapshot.emotion_score = event.analysis.emotion_score
        snapshot.emotion_label = event.analysis.emotion_label
        snapshot.recent_flags = list(dict.fromkeys(event.analysis.risk_flags))

        cards = dict(snapshot.cards or {})
        cards["cognitive_score"] = event.analysis.cognitive_score
        cards["emotion_trend"] = event.analysis.emotion_label
        cards["meds_tracker"] = 0 if "missed_meds" in event.analysis.risk_flags else 1
        cards["sleep_quality"] = "check" if event.analysis.emotion_score > 0.7 else "stable"
        cards["last_session_id"] = event.session_id
        cards["last_transcript_len"] = len(event.transcript.split())
        snapshot.cards = cards

        await session.commit()
        return await FamilyRepository.get_snapshot(session, event.user_id)

    @staticmethod
    async def get_snapshot(session: AsyncSession, user_id: str) -> DashboardSnapshot:
        snapshot = await session.get(DashboardSnapshotModel, user_id)
        if snapshot is None:
            return DashboardSnapshot(user_id=user_id)

        alert_rows = await session.execute(
            select(DashboardEvent)
            .where(
                DashboardEvent.user_id == user_id,
                DashboardEvent.alert_severity.in_([
                    AlertSeverity.warning.value,
                    AlertSeverity.critical.value,
                ]),
            )
            .order_by(desc(DashboardEvent.created_at))
            .limit(10)
        )

        active_alerts: list[AlertDecision] = []
        for row in alert_rows.scalars().all():
            if not row.alert_severity:
                continue
            active_alerts.append(
                AlertDecision(
                    severity=AlertSeverity(row.alert_severity),
                    notify_family=True,
                    reasons=list(row.alert_reasons or []),
                    sms_message=row.alert_message,
                    created_at=row.created_at.isoformat(),
                )
            )

        return DashboardSnapshot(
            user_id=user_id,
            last_updated=snapshot.last_updated.isoformat(),
            cognitive_score=snapshot.cognitive_score,
            emotion_score=snapshot.emotion_score,
            emotion_label=snapshot.emotion_label,
            recent_flags=list(snapshot.recent_flags or []),
            active_alerts=active_alerts,
            cards=dict(snapshot.cards or {}),
        )

    @staticmethod
    async def get_history(
        session: AsyncSession,
        user_id: str,
        limit: int = 50,
    ) -> list[DashboardIngestRequest]:
        rows = await session.execute(
            select(DashboardEvent)
            .where(DashboardEvent.user_id == user_id)
            .order_by(desc(DashboardEvent.created_at))
            .limit(limit)
        )

        history: list[DashboardIngestRequest] = []
        for row in rows.scalars().all():
            alert = None
            if row.alert_severity:
                alert = AlertDecision(
                    severity=AlertSeverity(row.alert_severity),
                    notify_family=row.alert_severity != AlertSeverity.none.value,
                    reasons=list(row.alert_reasons or []),
                    sms_message=row.alert_message,
                    created_at=row.created_at.isoformat(),
                )

            analysis = AnalysisResult(
                emotion_label=row.emotion_label,
                emotion_score=row.emotion_score,
                cognitive_score=row.cognitive_score,
                risk_flags=list(row.risk_flags or []),
                biomarkers=dict(row.biomarkers or {}),
                created_at=row.created_at.isoformat(),
            )
            history.append(
                DashboardIngestRequest(
                    session_id=row.session_id,
                    user_id=row.user_id,
                    transcript=row.transcript,
                    assistant_text=row.assistant_text,
                    analysis=analysis,
                    alert=alert,
                )
            )

        return history

    @staticmethod
    async def get_insights(
        session: AsyncSession,
        user_id: str,
        days: int = 30,
    ) -> DashboardInsights:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        rows = await session.execute(
            select(DashboardEvent)
            .where(
                DashboardEvent.user_id == user_id,
                DashboardEvent.created_at >= cutoff,
            )
            .order_by(desc(DashboardEvent.created_at))
            .limit(1000)
        )
        events = rows.scalars().all()
        total_turns = len(events)
        sessions_count = len({row.session_id for row in events})

        if not events:
            return DashboardInsights(
                user_id=user_id,
                window_days=days,
                summary="Δεν υπάρχουν ακόμη αρκετά δεδομένα συνομιλιών για συμπεράσματα.",
            )

        avg_emotion = sum(float(row.emotion_score or 0.0) for row in events) / total_turns
        avg_cognitive = sum(float(row.cognitive_score or 0.0) for row in events) / total_turns

        risk_counts: Counter[str] = Counter()
        alert_counts: Counter[str] = Counter()
        keyword_counts: Counter[str] = Counter()

        for row in events:
            risk_counts.update(str(flag) for flag in (row.risk_flags or []))
            if row.alert_severity:
                alert_counts.update([row.alert_severity])
            keyword_counts.update(_extract_keywords(row.transcript))

        top_keywords = [keyword for keyword, _ in keyword_counts.most_common(8)]
        suggested_actions = _build_suggested_actions(
            avg_emotion=avg_emotion,
            avg_cognitive=avg_cognitive,
            risk_counts=risk_counts,
            alert_counts=alert_counts,
        )
        summary = _build_summary(
            total_turns=total_turns,
            sessions_count=sessions_count,
            avg_emotion=avg_emotion,
            avg_cognitive=avg_cognitive,
            risk_counts=risk_counts,
            alert_counts=alert_counts,
        )

        return DashboardInsights(
            user_id=user_id,
            window_days=days,
            total_turns=total_turns,
            sessions_count=sessions_count,
            avg_emotion_score=round(avg_emotion, 3),
            avg_cognitive_score=round(avg_cognitive, 3),
            risk_flag_counts=_counter_to_sorted_dict(risk_counts),
            alert_counts=_counter_to_sorted_dict(alert_counts),
            top_keywords=top_keywords,
            suggested_actions=suggested_actions,
            summary=summary,
        )

    @staticmethod
    def to_user_view(user: User) -> UserView:
        return UserView(
            user_id=user.user_id,
            username=user.username,
            display_name=user.display_name,
            role=UserRole(user.role),
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
        )
