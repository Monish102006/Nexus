"""Shared helpers for NEXUS agents."""

from abc import ABC, abstractmethod

from ..config import settings
from ..core.llm import LLMError, llm_client


class BaseAgent(ABC):
    name: str = "agent"
    role: str = "Agent"
    description: str = ""

    @property
    def mode(self) -> str:
        return "demo" if not llm_client.available else "llm"

    async def run(self, context: dict) -> dict:  # pragma: no cover - interface
        raise NotImplementedError

    async def _try_llm(self, system_prompt: str, user_prompt: str) -> dict:
        """Call the LLM, surfacing failures so the caller can fall back."""
        return await llm_client.complete_json(system_prompt, user_prompt)

    @staticmethod
    def _clean_list(value, limit=12):
        if not isinstance(value, list):
            return []
        out = []
        for item in value:
            if isinstance(item, str):
                text = item.strip()
            elif isinstance(item, dict):
                text = "; ".join(
                    f"{k}: {v}" for k, v in item.items() if v not in (None, "")
                )
            else:
                text = str(item).strip()
            if text:
                out.append(text)
            if len(out) >= limit:
                break
        return out


def demo_banner() -> str:
    return (
        "Demo mode: deterministic analysis derived only from the objective. "
        "No external sources were fetched or fabricated."
        if settings.demo_mode
        else ""
    )
