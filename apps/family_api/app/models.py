from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), index=True)
    display_name: Mapped[str] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class DashboardEvent(Base):
    __tablename__ = "dashboard_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), index=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    transcript: Mapped[str] = mapped_column(Text)
    assistant_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    emotion_label: Mapped[str] = mapped_column(String(64))
    emotion_score: Mapped[float] = mapped_column(Float)
    cognitive_score: Mapped[float] = mapped_column(Float)
    risk_flags: Mapped[list[str]] = mapped_column(JSON, default=list)
    biomarkers: Mapped[dict] = mapped_column(JSON, default=dict)

    alert_severity: Mapped[str | None] = mapped_column(String(32), nullable=True)
    alert_reasons: Mapped[list[str]] = mapped_column(JSON, default=list)
    alert_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class DashboardSnapshotModel(Base):
    __tablename__ = "dashboard_snapshots"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    cognitive_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    emotion_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    emotion_label: Mapped[str | None] = mapped_column(String(64), nullable=True)
    recent_flags: Mapped[list[str]] = mapped_column(JSON, default=list)
    cards: Mapped[dict] = mapped_column(JSON, default=dict)
