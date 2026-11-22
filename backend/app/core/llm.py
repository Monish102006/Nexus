import json
import re

import httpx

from ..config import settings


class LLMError(Exception):
    """Raised when the LLM is unavailable or returns unusable output."""


def _extract_json(text: str) -> dict:
    if not text or not text.strip():
        raise LLMError("Empty LLM response")

    cleaned = text.strip()

    # Remove ```json ... ``` fences if present.
    fence = re.search(r"```(?:json)?\s*(.*?)```", cleaned, re.DOTALL)
    if fence:
        cleaned = fence.group(1).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Fall back to the outermost JSON object.
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = cleaned[start : end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as exc:
            raise LLMError(f"Malformed JSON from LLM: {exc}") from exc

    raise LLMError("No JSON object found in LLM response")


class LLMClient:
    """Minimal OpenAI-compatible chat client that returns structured JSON."""

    def __init__(self):
        self.api_key = settings.llm_api_key
        self.base_url = settings.llm_base_url
        self.model = settings.llm_model
        self.timeout = settings.llm_timeout

    @property
    def available(self) -> bool:
        return bool(self.api_key) and not settings.force_demo

    async def complete_json(self, system_prompt: str, user_prompt: str) -> dict:
        if not self.available:
            raise LLMError("LLM credentials are not configured")

        payload = {
            "model": self.model,
            "temperature": 0.3,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        url = f"{self.base_url}/chat/completions"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
        except httpx.HTTPError as exc:
            raise LLMError(f"LLM request failed: {exc}") from exc

        if response.status_code >= 400:
            raise LLMError(
                f"LLM returned HTTP {response.status_code}: {response.text[:300]}"
            )

        try:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError) as exc:
            raise LLMError(f"Unexpected LLM response shape: {exc}") from exc

        return _extract_json(content)


llm_client = LLMClient()
