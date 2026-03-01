from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from apps.family_api.app.config import settings
from apps.family_api.app.models import Base

engine = create_async_engine(settings.database_url, future=True, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db() -> None:
    attempts = 10
    for attempt in range(1, attempts + 1):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                # Lightweight migration for older local databases.
                await conn.execute(
                    text(
                        "ALTER TABLE dashboard_events "
                        "ADD COLUMN IF NOT EXISTS assistant_text TEXT"
                    )
                )
            return
        except Exception as exc:
            if attempt == attempts:
                raise
            print(f"[family-api] waiting for database ({attempt}/{attempts}): {exc}")
            await asyncio.sleep(2)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
