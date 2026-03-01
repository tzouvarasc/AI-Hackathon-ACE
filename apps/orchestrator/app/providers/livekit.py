from __future__ import annotations

from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse, urlunparse

import httpx
import jwt


class LiveKitProvider:
    """Generates LiveKit tokens and calls SIP administration APIs."""

    def __init__(self, api_key: str, api_secret: str, ws_url: str) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.ws_url = ws_url

    def create_participant_token(
        self,
        identity: str,
        room_name: str,
        ttl_seconds: int = 3600,
    ) -> str:
        if not self.api_key or not self.api_secret:
            raise RuntimeError("Missing LIVEKIT_API_KEY/LIVEKIT_API_SECRET")

        now = datetime.now(timezone.utc)
        payload = {
            "iss": self.api_key,
            "sub": identity,
            "nbf": int((now - timedelta(seconds=5)).timestamp()),
            "exp": int((now + timedelta(seconds=ttl_seconds)).timestamp()),
            "video": {
                "roomJoin": True,
                "room": room_name,
                "canPublish": True,
                "canSubscribe": True,
            },
        }
        return jwt.encode(payload, self.api_secret, algorithm="HS256")

    async def create_sip_dispatch_rule(
        self,
        inbound_trunk_id: str,
        room_prefix: str,
        metadata: str,
        timeout_seconds: float,
    ) -> str:
        if not inbound_trunk_id:
            raise RuntimeError("Missing inbound trunk id for SIP dispatch rule")

        body = await self._post_twirp(
            method="CreateSIPDispatchRule",
            payload={
                "rule": {
                    "dispatchRuleIndividual": {"roomPrefix": room_prefix},
                    "trunkIds": [inbound_trunk_id],
                    "metadata": metadata or "",
                }
            },
            timeout_seconds=timeout_seconds,
        )

        dispatch_rule_id = (
            body.get("sipDispatchRuleId")
            or body.get("dispatchRuleId")
            or body.get("rule", {}).get("sipDispatchRuleId")
            or body.get("rule", {}).get("id")
            or ""
        )
        if not dispatch_rule_id:
            raise RuntimeError("LiveKit SIP dispatch response missing dispatch rule id")
        return str(dispatch_rule_id)

    async def create_sip_participant(
        self,
        sip_trunk_id: str,
        to_number: str,
        room_name: str,
        participant_identity: str,
        participant_name: str,
        timeout_seconds: float,
    ) -> tuple[str, str]:
        if not sip_trunk_id:
            raise RuntimeError("Missing outbound SIP trunk id")

        body = await self._post_twirp(
            method="CreateSIPParticipant",
            payload={
                "sipTrunkId": sip_trunk_id,
                "sipCallTo": to_number,
                "roomName": room_name,
                "participantIdentity": participant_identity,
                "participantName": participant_name,
            },
            timeout_seconds=timeout_seconds,
        )

        sip_call_id = (
            body.get("sipCallId")
            or body.get("callId")
            or body.get("participant", {}).get("sipCallId")
            or f"sip-{room_name}"
        )
        identity = str(body.get("participantIdentity") or participant_identity)
        return str(sip_call_id), identity

    async def _post_twirp(self, method: str, payload: dict, timeout_seconds: float) -> dict:
        if not self.api_key or not self.api_secret:
            raise RuntimeError("Missing LIVEKIT_API_KEY/LIVEKIT_API_SECRET")

        url = f"{self._server_api_base_url()}/twirp/livekit.SIP/{method}"
        headers = {
            "Authorization": f"Bearer {self._create_server_token()}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

    def _create_server_token(self, ttl_seconds: int = 600) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "iss": self.api_key,
            "nbf": int((now - timedelta(seconds=5)).timestamp()),
            "exp": int((now + timedelta(seconds=ttl_seconds)).timestamp()),
            "video": {
                "roomCreate": True,
                "roomList": True,
                "roomAdmin": True,
            },
            "sip": {
                "admin": True,
                "call": True,
            },
        }
        return jwt.encode(payload, self.api_secret, algorithm="HS256")

    def _server_api_base_url(self) -> str:
        if "://" not in self.ws_url:
            return f"https://{self.ws_url.strip('/')}"

        parsed = urlparse(self.ws_url)
        if parsed.scheme in {"ws", "wss"}:
            scheme = "https" if parsed.scheme == "wss" else "http"
            return urlunparse((scheme, parsed.netloc, "", "", "", "")).rstrip("/")

        if parsed.scheme in {"http", "https"}:
            return urlunparse((parsed.scheme, parsed.netloc, "", "", "", "")).rstrip("/")

        return self.ws_url.rstrip("/")
