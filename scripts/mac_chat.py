#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Any


def post_json(url: str, payload: dict[str, Any], timeout: float = 25.0) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8").strip()
        return json.loads(raw) if raw else {}


def maybe_play_audio(audio_chunk_ref: str) -> bool:
    if not audio_chunk_ref.startswith("file://"):
        return False

    path = audio_chunk_ref.replace("file://", "", 1)
    if not os.path.isfile(path):
        return False

    try:
        subprocess.Popen(
            ["afplay", path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except Exception:
        return False


def create_session(orchestrator_url: str, user_id: str, channel: str, locale: str) -> str:
    payload = {
        "user_id": user_id,
        "channel": channel,
        "locale": locale,
    }
    response = post_json(f"{orchestrator_url}/v1/sessions/start", payload)
    session_id = str(response.get("session_id") or "").strip()
    if not session_id:
        raise RuntimeError(f"Could not create session: {response}")
    return session_id


def process_turn(orchestrator_url: str, session_id: str, user_id: str, text: str) -> dict[str, Any]:
    payload = {
        "session_id": session_id,
        "user_id": user_id,
        "raw_text": text,
    }
    return post_json(f"{orchestrator_url}/v1/turns/process", payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Text chat with Thalpo from your Mac terminal.")
    parser.add_argument("--orchestrator-url", default="http://localhost:8000", help="Orchestrator base URL")
    parser.add_argument("--user-id", default="mac-user", help="User id for the conversation")
    parser.add_argument("--locale", default="el-GR", help="Locale for session start")
    parser.add_argument("--channel", default="pstn", choices=["pstn", "webrtc"], help="Session channel")
    parser.add_argument("--session-id", default="", help="Optional existing session id")
    parser.add_argument("--play-audio", action="store_true", help="Play generated MP3 locally with afplay")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    orchestrator_url = args.orchestrator_url.rstrip("/")

    try:
        session_id = args.session_id.strip() or create_session(
            orchestrator_url=orchestrator_url,
            user_id=args.user_id,
            channel=args.channel,
            locale=args.locale,
        )
    except urllib.error.URLError as exc:
        print(f"Failed to connect to orchestrator: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Session init failed: {exc}", file=sys.stderr)
        return 1

    print(f"Connected to Thalpo. session_id={session_id}")
    print("Type your message. Use /exit to quit.")

    while True:
        try:
            user_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            return 0

        if not user_text:
            continue
        if user_text.lower() in {"/exit", "/quit", "exit", "quit"}:
            print("Bye.")
            return 0

        try:
            response = process_turn(
                orchestrator_url=orchestrator_url,
                session_id=session_id,
                user_id=args.user_id,
                text=user_text,
            )
        except urllib.error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="ignore")
            print(f"Request failed ({exc.code}): {details}", file=sys.stderr)
            continue
        except urllib.error.URLError as exc:
            print(f"Network error: {exc}", file=sys.stderr)
            continue
        except Exception as exc:
            print(f"Unexpected error: {exc}", file=sys.stderr)
            continue

        assistant_text = str(response.get("assistant_text") or "").strip()
        total_ms = response.get("latency_ms", {}).get("total")
        audio_chunk_ref = str(response.get("audio_chunk_ref") or "")

        print(f"Thalpo: {assistant_text or '(no reply)'}")
        if isinstance(total_ms, int):
            print(f"Latency: {total_ms}ms")

        if args.play_audio:
            played = maybe_play_audio(audio_chunk_ref)
            if not played and audio_chunk_ref:
                print(f"Audio not played: {audio_chunk_ref}")


if __name__ == "__main__":
    raise SystemExit(main())
