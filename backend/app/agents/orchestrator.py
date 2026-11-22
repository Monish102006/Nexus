"""NEXUS orchestrator — coordinates the specialised agents in sequence."""

import json
import logging

from sqlalchemy.orm import Session

from ..config import settings
from ..models import Activity, AgentResult, Approval, Mission, Task, utcnow
from ..services.telegram_chats import latest_known_chat_id
from .communication import CommunicationAgent
from .planning import PlanningAgent
from .research import ResearchAgent

logger = logging.getLogger("nexus.orchestrator")


class Orchestrator:
    def __init__(self):
        self.research_agent = ResearchAgent()
        self.planning_agent = PlanningAgent()
        self.communication_agent = CommunicationAgent()

    async def execute(self, db: Session, mission: Mission) -> Mission:
        try:
            mission.status = "running"
            mission.updated_at = utcnow()
            db.commit()
            self._log(
                db,
                mission,
                "mission_created",
                f"Mission accepted from {mission.source}: {mission.objective[:140]}",
                "info",
            )

            context = {"objective": mission.objective}

            research = await self._run_agent(
                db, mission, self.research_agent, context
            )
            context["research"] = research

            plan = await self._run_agent(
                db, mission, self.planning_agent, context
            )
            context["plan"] = plan

            communication = await self._run_agent(
                db, mission, self.communication_agent, context
            )
            context["communication"] = communication

            tasks = self._persist_tasks(db, mission, plan)
            approval = self._create_approval(db, mission, communication)

            mission.status = "awaiting_approval"
            mission.summary = self._build_summary(plan, tasks, approval)
            mission.updated_at = utcnow()
            db.commit()

            self._log(
                db,
                mission,
                "approval_requested",
                "Telegram announcement drafted and is awaiting human approval.",
                "warning",
            )
            return mission

        except Exception as exc:  # noqa: BLE001 - surface failure honestly
            logger.exception("Mission execution failed")
            db.rollback()
            failed = db.get(Mission, mission.id)
            if failed is not None:
                failed.status = "failed"
                failed.error = str(exc)[:500]
                failed.updated_at = utcnow()
                db.commit()
                self._log(
                    db, failed, "mission_failed", f"Mission failed: {exc}", "error"
                )
                return failed
            raise

    async def _run_agent(self, db, mission, agent, context):
        self._log(
            db, mission, "agent_started", f"{agent.role} started.", "info"
        )
        output = await agent.run(context)
        result = AgentResult(
            mission_id=mission.id,
            agent_name=agent.name,
            role=agent.role,
            status="completed",
            source=str(output.get("source", "demo")),
            output=json.dumps(output, default=str),
        )
        db.add(result)
        mission.updated_at = utcnow()
        db.commit()
        self._log(
            db,
            mission,
            "agent_completed",
            f"{agent.role} produced structured output "
            f"({output.get('source', 'demo')} mode).",
            "success",
        )
        return output

    def _persist_tasks(self, db, mission, plan):
        tasks = []
        for index, item in enumerate(plan.get("tasks") or []):
            task = Task(
                mission_id=mission.id,
                title=str(item.get("title") or f"Task {index + 1}")[:300],
                description=str(item.get("description") or ""),
                priority=str(item.get("priority") or "medium"),
                deadline=str(item.get("deadline") or ""),
                dependency=item.get("depends_on"),
                status="pending",
                order_index=index,
            )
            db.add(task)
            tasks.append(task)
        db.commit()
        return tasks

    def _create_approval(self, db, mission, communication):
        action = communication.get("action") or {}
        content = (
            communication.get("announcement")
            or action.get("content")
            or ""
        ).strip()
        if not content:
            raise ValueError("Communication agent produced no announcement content")

        target = mission.source_chat_id or (
            str(settings.telegram_default_chat_id)
            if settings.telegram_default_chat_id is not None
            else None
        )
        if target is None:
            target = latest_known_chat_id(db)
        if target is None and len(settings.telegram_allowed_chat_ids) == 1:
            target = str(settings.telegram_allowed_chat_ids[0])

        approval = Approval(
            mission_id=mission.id,
            action_type=str(action.get("type") or "telegram_send"),
            channel=str(action.get("channel") or "telegram"),
            content=content,
            status="pending",
            target_chat_id=target,
        )
        db.add(approval)
        db.commit()
        db.refresh(approval)
        return approval

    def _build_summary(self, plan, tasks, approval):
        plan_summary = str(plan.get("summary") or "").strip()
        horizon = plan.get("horizon_days", "?")
        if not plan_summary:
            plan_summary = f"{len(tasks)} tasks were generated."
        return (
            f"{plan_summary} {len(tasks)} tasks scheduled across {horizon} days. "
            f"A Telegram announcement is awaiting human approval."
        )

    def _log(self, db, mission, activity_type, message, level="info"):
        db.add(
            Activity(
                mission_id=mission.id,
                type=activity_type,
                message=message,
                level=level,
            )
        )
        db.commit()


orchestrator = Orchestrator()
