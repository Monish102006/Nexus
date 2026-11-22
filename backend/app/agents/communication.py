"""Communication Agent — drafts objective-specific Telegram messages.

It never sends; the orchestrator turns its action payload into a pending approval.
"""

from .base import BaseAgent, demo_banner
from .domains import get_profile
from ..core.llm import LLMError

SYSTEM_PROMPT = """You are the Communication Agent inside NEXUS. Using the objective
and plan, write a polished Telegram announcement that will be sent after human
approval.

Rules:
- Return ONLY valid JSON with this exact shape:
{
  "announcement": "the full Telegram message",
  "summary": "one sentence describing the message",
  "tone": "professional"
}
- The announcement must be specific to the objective's actual domain.
- Do NOT use event-planning language (venues, agendas, registration) unless the
  objective explicitly concerns an event.
- The announcement must be ready to send as-is.
- Use at most 2 emojis, short paragraphs and a clear call to action.
- Do not claim the message has been sent. Do not include approval instructions.
- Do not fabricate links, prices or dates that are not in the plan."""


class CommunicationAgent(BaseAgent):
    name = "communication"
    role = "Communication Agent"
    description = "Drafts Telegram announcements and action payloads for approval."

    async def run(self, context: dict) -> dict:
        objective = context["objective"]
        plan = context.get("plan") or {}
        research = context.get("research") or {}
        profile = get_profile(objective)
        if self.mode == "llm":
            try:
                data = await self._try_llm(
                    SYSTEM_PROMPT,
                    "Objective:\n"
                    f"{objective}\n\n"
                    f"Detected domain: {profile['label']}. Keep the message "
                    "specific to this domain; do not use event language unless "
                    "the objective is an event.\n\n"
                    f"Research:\n{research}\n\nPlan:\n{plan}\n\n"
                    "Return the JSON now.",
                )
                return self._normalise(data, objective, profile, source="llm")
            except LLMError as exc:
                fallback = self._fallback(objective, plan, research, profile)
                fallback["note"] = (
                    f"LLM unavailable, used deterministic announcement: {exc}"
                )
                return fallback
        return self._fallback(objective, plan, research, profile)

    def _normalise(self, data: dict, objective: str, profile: dict, source: str) -> dict:
        announcement = str(data.get("announcement") or "").strip()
        if not announcement:
            raise LLMError("Communication agent returned an empty announcement")
        return {
            "objective": objective,
            "domain": profile["domain"],
            "announcement": announcement,
            "summary": str(data.get("summary") or "").strip(),
            "tone": str(data.get("tone") or "professional").strip(),
            "source": source,
            "action": {
                "type": "telegram_send",
                "channel": "telegram",
                "content": announcement,
            },
        }

    def _fallback(self, objective: str, plan: dict, research: dict, profile: dict) -> dict:
        comm = profile["communication"]
        tasks = plan.get("tasks") or []
        horizon = plan.get("horizon_days")

        title = objective.strip().rstrip(".")
        if title:
            title = title[0].upper() + title[1:]

        lines = [comm["intro"].format(objective=title), ""]
        if horizon and "{horizon}" not in comm["lead"]:
            lines.append(f"Timeline: {horizon} days.")
        lines.append(
            comm["lead"].format(
                horizon=horizon if horizon else "the planned timeframe"
            )
        )

        if tasks:
            lines.append("")
            lines.append("What happens next:")
            for task in tasks[:4]:
                label = task.get("title") or "Next step"
                deadline = task.get("deadline")
                suffix = f" — by {deadline}" if deadline else ""
                lines.append(f"• {label}{suffix}")

        risks = research.get("risks") or []
        if risks:
            lines.append("")
            lines.append(f"Note: {risks[0]}.")

        lines.append("")
        lines.append(comm["cta"])
        announcement = "\n".join(lines)

        return {
            "objective": objective,
            "domain": profile["domain"],
            "announcement": announcement,
            "summary": comm["summary"],
            "tone": "professional",
            "source": "demo",
            "note": demo_banner(),
            "action": {
                "type": "telegram_send",
                "channel": "telegram",
                "content": announcement,
            },
        }
