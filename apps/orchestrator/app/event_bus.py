from __future__ import annotations

import json

import redis.asyncio as redis

from shared.contracts.schemas import VoiceTurnEvent


class TurnEventBus:
    def __init__(self, redis_url: str, stream_name: str) -> None:
        self.stream_name = stream_name
        self.client = redis.from_url(redis_url, decode_responses=True)

    async def publish_turn_event(self, event: VoiceTurnEvent) -> str | None:
        try:
            payload = json.dumps(event.model_dump(mode="json"))
            message_id = await self.client.xadd(
                self.stream_name,
                {"payload": payload},
                maxlen=10000,
                approximate=True,
            )
            return message_id
        except Exception as exc:  # pragma: no cover - infrastructure path
            print(f"[event-bus] Redis xadd failed: {exc}")
            return None

    async def close(self) -> None:
        try:
            await self.client.close()
        except Exception:
            pass
