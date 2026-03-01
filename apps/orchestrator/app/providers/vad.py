from __future__ import annotations


class VADProvider:
    """MVP VAD placeholder. Replace with Silero/WebRTC VAD frame-level handling."""

    @staticmethod
    def detect(raw_text: str) -> tuple[bool, int]:
        has_voice = bool(raw_text and raw_text.strip())
        return has_voice, 30
