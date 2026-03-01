from __future__ import annotations

import time

import httpx


class LLMProvider:
    """LLM provider with Azure OpenAI or OpenAI support and deterministic fallback."""

    def __init__(
        self,
        provider: str,
        api_key: str,
        model: str,
        timeout_seconds: float,
        azure_api_key: str = "",
        azure_endpoint: str = "",
        azure_deployment: str = "",
        azure_api_version: str = "2024-10-21",
    ) -> None:
        self.provider = (provider or "openai").strip().lower()
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.azure_api_key = azure_api_key
        self.azure_endpoint = azure_endpoint.rstrip("/")
        self.azure_deployment = azure_deployment
        self.azure_api_version = azure_api_version

    async def generate_reply(self, transcript: str, locale: str = "el-GR") -> tuple[str, int]:
        if not transcript.strip():
            if self._is_greek(locale):
                return "Δεν σας άκουσα καλά. Μπορείτε να το πείτε πιο αργά;", 180
            return "I did not catch that. Please repeat slowly.", 180

        system_prompt = (
            "You are Thalpo, a calm and safety-aware elderly care voice companion. "
            "Respond in short, empathetic sentences. If user may be in danger, "
            "offer immediate grounding and ask permission to alert family. "
            "Do not quote or repeat the user's sentence verbatim. "
            "Do not start with 'I heard you say' or equivalent phrases. "
            f"Preferred locale: {locale}."
        )

        if self.provider == "azure":
            return await self._generate_reply_azure(transcript=transcript, locale=locale, system_prompt=system_prompt)

        if not self.api_key:
            return self._fallback_reply(transcript, locale), 250

        return await self._generate_reply_openai(transcript=transcript, locale=locale, system_prompt=system_prompt)

    async def _generate_reply_openai(
        self,
        transcript: str,
        locale: str,
        system_prompt: str,
    ) -> tuple[str, int]:
        start = time.perf_counter()

        payload = {
            "model": self.model,
            "input": [
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": system_prompt}],
                },
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": transcript}],
                },
            ],
            "temperature": 0.35,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    "https://api.openai.com/v1/responses",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()

            reply = (data.get("output_text") or "").strip()
            if not reply:
                reply = self._fallback_reply(transcript, locale)
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            return reply, max(elapsed_ms, 220)
        except Exception as exc:  # pragma: no cover - integration path
            print(f"[llm] OpenAI generation failed: {exc}")
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            return self._fallback_reply(transcript, locale), max(elapsed_ms, 220)

    async def _generate_reply_azure(
        self,
        transcript: str,
        locale: str,
        system_prompt: str,
    ) -> tuple[str, int]:
        start = time.perf_counter()

        if not (self.azure_api_key and self.azure_endpoint and self.azure_deployment):
            print("[llm] Azure provider selected but AZURE_OPENAI_* env is incomplete.")
            return self._fallback_reply(transcript, locale), 250

        url = (
            f"{self.azure_endpoint}/openai/deployments/{self.azure_deployment}"
            f"/chat/completions?api-version={self.azure_api_version}"
        )
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": transcript},
            ],
            "temperature": 0.35,
            "max_tokens": 220,
        }
        headers = {
            "api-key": self.azure_api_key,
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

            content = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )
            if isinstance(content, list):
                parts: list[str] = []
                for item in content:
                    if not isinstance(item, dict):
                        continue
                    text = item.get("text") or item.get("content")
                    if isinstance(text, str) and text.strip():
                        parts.append(text.strip())
                reply = "\n".join(parts).strip()
            else:
                reply = str(content or "").strip()

            if not reply:
                reply = self._fallback_reply(transcript, locale)

            elapsed_ms = int((time.perf_counter() - start) * 1000)
            return reply, max(elapsed_ms, 220)
        except Exception as exc:  # pragma: no cover - integration path
            print(f"[llm] Azure generation failed: {exc}")
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            return self._fallback_reply(transcript, locale), max(elapsed_ms, 220)

    @staticmethod
    def _is_greek(locale: str) -> bool:
        return (locale or "").lower().startswith("el")

    def _fallback_reply(self, transcript: str, locale: str) -> str:
        lowered = " ".join(transcript.split()).strip().lower()

        med_hit = any(token in lowered for token in ["medicine", "pill", "med", "φαρμακ", "χαπι"])
        distress_hit = any(
            token in lowered
            for token in ["afraid", "panic", "help", "φοβα", "βοηθ", "πανικ", "ζαλ", "πονο"]
        )

        if self._is_greek(locale):
            if med_hit:
                return "Σε ακούω. Να δούμε μαζί τα φάρμακά σας; Θέλετε να σας το θυμίσω τώρα;"
            if distress_hit:
                return "Είμαι εδώ μαζί σας. Πάρτε μια αργή ανάσα. Θέλετε να ειδοποιήσω την οικογένειά σας;"
            if "ποδι" in lowered or "πονά" in lowered or "πονος" in lowered:
                return "Λυπάμαι που πονάτε. Ο πόνος είναι έντονος τώρα ή ήπιος; Θέλετε να κάνουμε ένα μικρό check;"
            return "Ευχαριστώ που το μοιραστήκατε. Πώς νιώθετε αυτή τη στιγμή; Είμαι εδώ να βοηθήσω βήμα-βήμα."

        if med_hit:
            return (
                "I hear you. Let us check your medication together. "
                "Would you like me to remind you now?"
            )
        if distress_hit:
            return (
                "I am here with you. Take a slow breath with me. "
                "I can notify your family if you want."
            )
        return (
            "Thank you for sharing. Tell me how you are feeling right now, "
            "and I will support you step by step."
        )
