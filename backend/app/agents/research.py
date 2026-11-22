"""Research Agent — extracts requirements, constraints and gaps."""

import re

from .base import BaseAgent, demo_banner
from .domains import get_profile
from ..core.llm import LLMError

SYSTEM_PROMPT = """You are the Research Agent inside NEXUS, an autonomous mission
control system. Analyse the objective and extract concrete requirements,
constraints, missing information, risks and assumptions.

Rules:
- Return ONLY valid JSON with this exact shape:
{
  "requirements": ["..."],
  "constraints": ["..."],
  "missing_information": ["..."],
  "risks": ["..."],
  "assumptions": ["..."],
  "research_notes": "short note"
}
- Keep everything specific to the objective's actual domain.
- Do NOT fabricate sources, statistics, links or external research.
- Do NOT use event-planning language (venues, agendas, registration) unless the
  objective explicitly concerns an event.
- Base everything strictly on the objective and reasonable operational reasoning.
- Be specific and concise. Max 6 items per list."""


class ResearchAgent(BaseAgent):
    name = "research"
    role = "Research Agent"
    description = "Extracts requirements, constraints and missing information."

    async def run(self, context: dict) -> dict:
        objective = context["objective"]
        profile = get_profile(objective)
        if self.mode == "llm":
            try:
                data = await self._try_llm(
                    SYSTEM_PROMPT,
                    f"Objective:\n{objective}\n\n"
                    f"Detected domain: {profile['label']}. Keep the analysis "
                    "specific to this domain. Do not use unrelated event-planning "
                    "content unless the objective is an event.\n\n"
                    "Return the JSON now.",
                )
                return self._normalise(data, objective, profile, source="llm")
            except LLMError as exc:
                fallback = self._fallback(objective, profile)
                fallback["note"] = (
                    f"LLM unavailable, used deterministic research: {exc}"
                )
                return fallback
        return self._fallback(objective, profile)

    def _normalise(self, data: dict, objective: str, profile: dict, source: str) -> dict:
        return {
            "objective": objective,
            "domain": profile["domain"],
            "requirements": self._clean_list(data.get("requirements")),
            "constraints": self._clean_list(data.get("constraints")),
            "missing_information": self._clean_list(
                data.get("missing_information")
            ),
            "risks": self._clean_list(data.get("risks")),
            "assumptions": self._clean_list(data.get("assumptions")),
            "research_notes": str(data.get("research_notes") or "").strip(),
            "source": source,
        }

    def _fallback(self, objective: str, profile: dict) -> dict:
        lower = objective.lower()
        constraints = []

        numbers = re.findall(
            r"(\d[\d,]*)\s*(students|people|participants|attendees|days|weeks|hours|"
            r"speakers|mentors|teams|users|budget|subscribers)",
            lower,
        )
        for amount, unit in numbers:
            constraints.append(f"{amount} {unit} mentioned as a scope constraint")

        days = re.search(r"within\s+(\d+)\s+day", lower)
        if days:
            constraints.append(f"Delivery deadline is within {days.group(1)} days")

        for item in profile["constraints"]:
            if item not in constraints:
                constraints.append(item)

        if not constraints:
            constraints.append("Scope and success metrics are not quantified")

        notes = demo_banner()
        if not notes:
            notes = (
                "Requirements derived from the objective for a "
                f"{profile['label']}."
            )

        return {
            "objective": objective,
            "domain": profile["domain"],
            "requirements": list(profile["requirements"]),
            "constraints": constraints,
            "missing_information": list(profile["missing_information"]),
            "risks": list(profile["risks"]),
            "assumptions": list(profile["assumptions"]),
            "research_notes": notes,
            "source": "demo",
        }
