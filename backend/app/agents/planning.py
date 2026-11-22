"""Planning Agent — turns research into a sequenced, domain-aware task plan."""

import re
from datetime import date, timedelta

from .base import BaseAgent, demo_banner
from .domains import get_profile
from ..core.llm import LLMError

SYSTEM_PROMPT = """You are the Planning Agent inside NEXUS. Given an objective and
research findings, produce an executable plan with tasks, priorities, deadlines
and dependencies.

Rules:
- Return ONLY valid JSON with this exact shape:
{
  "summary": "one or two sentences",
  "horizon_days": 10,
  "tasks": [
    {
      "title": "short imperative task",
      "description": "what to do",
      "priority": "high|medium|low",
      "deadline": "YYYY-MM-DD",
      "depends_on": "title of a previous task or null"
    }
  ]
}
- Keep tasks specific to the objective's actual domain.
- Do NOT use event-planning tasks (venues, agendas, registration) unless the
  objective explicitly concerns an event.
- 5 to 8 tasks, ordered logically.
- Every dependency must reference the title of an earlier task.
- Deadlines must fall within the horizon and be ISO dates.
- Be realistic and specific. Do not invent external facts."""


class PlanningAgent(BaseAgent):
    name = "planning"
    role = "Planning Agent"
    description = "Generates tasks, priorities, deadlines and dependencies."

    async def run(self, context: dict) -> dict:
        objective = context["objective"]
        research = context.get("research") or {}
        profile = get_profile(objective)
        if self.mode == "llm":
            try:
                data = await self._try_llm(
                    SYSTEM_PROMPT,
                    "Objective:\n"
                    f"{objective}\n\n"
                    f"Detected domain: {profile['label']}. Keep tasks specific "
                    "to this domain; do not use event-planning tasks unless the "
                    "objective is an event.\n\n"
                    f"Research findings:\n{research}\n\n"
                    "Return the JSON now.",
                )
                return self._normalise(data, objective, research, profile, source="llm")
            except LLMError as exc:
                fallback = self._fallback(objective, research, profile)
                fallback["note"] = (
                    f"LLM unavailable, used deterministic plan: {exc}"
                )
                return fallback
        return self._fallback(objective, research, profile)

    def _normalise(
        self, data: dict, objective: str, research: dict, profile: dict, source: str
    ) -> dict:
        horizon = data.get("horizon_days")
        try:
            horizon = int(horizon)
        except (TypeError, ValueError):
            horizon = self._infer_horizon(research, objective)
        horizon = max(1, min(horizon, 365))

        tasks = []
        seen_titles = []
        raw_tasks = data.get("tasks") if isinstance(data.get("tasks"), list) else []
        for index, item in enumerate(raw_tasks[:10]):
            if not isinstance(item, dict):
                continue
            title = str(item.get("title") or f"Task {index + 1}").strip()
            depends_on = item.get("depends_on")
            if depends_on and depends_on not in seen_titles:
                depends_on = seen_titles[-1] if seen_titles else None
            priority = str(item.get("priority") or "medium").lower()
            if priority not in {"high", "medium", "low"}:
                priority = "medium"
            tasks.append(
                {
                    "title": title,
                    "description": str(item.get("description") or "").strip(),
                    "priority": priority,
                    "deadline": self._safe_deadline(item.get("deadline"), horizon),
                    "depends_on": depends_on,
                    "order": index + 1,
                }
            )
            seen_titles.append(title)

        if not tasks:
            return self._fallback(objective, research, profile)

        return {
            "objective": objective,
            "domain": profile["domain"],
            "summary": str(data.get("summary") or "").strip(),
            "horizon_days": horizon,
            "tasks": tasks,
            "source": source,
        }

    def _safe_deadline(self, value, horizon):
        try:
            parsed = date.fromisoformat(str(value))
            return parsed.isoformat()
        except (TypeError, ValueError):
            return (date.today() + timedelta(days=horizon)).isoformat()

    def _infer_horizon(self, research: dict, objective: str = "") -> int:
        text = " ".join(
            str(x)
            for x in (research.get("constraints") or [])
            + (research.get("requirements") or [])
        )
        text = f"{text} {objective}".lower()

        match = re.search(r"within\s+(\d+)\s+day", text)
        if match:
            return max(1, int(match.group(1)))
        match = re.search(r"in\s+(\d+)\s+day", text)
        if match:
            return max(1, int(match.group(1)))
        match = re.search(r"(\d+)[\s-]day", text)
        if match:
            return max(1, int(match.group(1)))
        match = re.search(r"(\d+)\s+week", text)
        if match:
            return max(1, int(match.group(1)) * 7)
        match = re.search(r"(\d+)[\s-]hour", text)
        if match:
            return max(1, round(int(match.group(1)) / 24))
        return 14

    def _fallback(self, objective: str, research: dict, profile: dict) -> dict:
        horizon = self._infer_horizon(research, objective)
        today = date.today()
        tasks = []
        for index, template in enumerate(profile["tasks"]):
            offset = max(0, round(horizon * template["fraction"]))
            tasks.append(
                {
                    "title": template["title"],
                    "description": template["description"],
                    "priority": template["priority"],
                    "deadline": (today + timedelta(days=offset)).isoformat(),
                    "depends_on": template["depends_on"],
                    "order": index + 1,
                }
            )

        return {
            "objective": objective,
            "domain": profile["domain"],
            "summary": (
                f"A {len(tasks)}-step {profile['label']} plan to deliver the "
                f"objective within {horizon} days."
            ),
            "horizon_days": horizon,
            "tasks": tasks,
            "source": "demo",
            "note": demo_banner(),
        }
