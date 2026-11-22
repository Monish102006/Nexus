"""Mission persistence and serialisation helpers."""

import json

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models import Activity, AgentResult, Approval, Mission, Task, utcnow


def create_mission(
    db: Session,
    objective: str,
    source: str = "web",
    source_chat_id: str | None = None,
) -> Mission:
    mission = Mission(
        objective=objective.strip(),
        status="pending",
        source=source,
        source_chat_id=str(source_chat_id) if source_chat_id else None,
    )
    db.add(mission)
    db.commit()
    db.refresh(mission)
    return mission


async def run_mission(db: Session, mission: Mission) -> Mission:
    # Imported lazily to keep module dependencies acyclic.
    from ..agents.orchestrator import orchestrator

    return await orchestrator.execute(db, mission)


def _parse_output(raw):
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return {"raw": raw}


def serialize_task(task: Task) -> dict:
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "deadline": task.deadline,
        "dependency": task.dependency,
        "status": task.status,
        "order_index": task.order_index,
    }


def serialize_agent_result(result: AgentResult) -> dict:
    return {
        "id": result.id,
        "agent_name": result.agent_name,
        "role": result.role,
        "status": result.status,
        "source": result.source,
        "output": _parse_output(result.output),
        "error": result.error,
        "created_at": result.created_at,
    }


def serialize_approval(approval: Approval) -> dict:
    return {
        "id": approval.id,
        "mission_id": approval.mission_id,
        "mission_objective": approval.mission.objective
        if approval.mission
        else None,
        "action_type": approval.action_type,
        "channel": approval.channel,
        "content": approval.content,
        "status": approval.status,
        "target_chat_id": approval.target_chat_id,
        "telegram_message_id": approval.telegram_message_id,
        "execution_note": approval.execution_note,
        "send_attempted": approval.send_attempted,
        "created_at": approval.created_at,
        "decided_at": approval.decided_at,
        "executed_at": approval.executed_at,
    }


def serialize_activity(activity: Activity) -> dict:
    return {
        "id": activity.id,
        "mission_id": activity.mission_id,
        "mission_objective": activity.mission.objective
        if activity.mission
        else None,
        "type": activity.type,
        "message": activity.message,
        "level": activity.level,
        "created_at": activity.created_at,
    }


def serialize_mission(mission: Mission, detail: bool = True) -> dict:
    latest_approval = mission.approvals[-1] if mission.approvals else None
    data = {
        "id": mission.id,
        "objective": mission.objective,
        "status": mission.status,
        "summary": mission.summary,
        "source": mission.source,
        "source_chat_id": mission.source_chat_id,
        "error": mission.error,
        "created_at": mission.created_at,
        "updated_at": mission.updated_at,
        "task_count": len(mission.tasks),
        "completed_task_count": sum(
            1 for task in mission.tasks if task.status == "completed"
        ),
        "agent_count": len(mission.agent_results),
        "approval_status": latest_approval.status if latest_approval else None,
        "latest_approval_id": latest_approval.id if latest_approval else None,
    }
    if detail:
        data["tasks"] = [serialize_task(t) for t in mission.tasks]
        data["agent_results"] = [
            serialize_agent_result(r) for r in mission.agent_results
        ]
        data["approvals"] = [serialize_approval(a) for a in mission.approvals]
        data["activity"] = [serialize_activity(a) for a in mission.activities]
    return data


def list_missions(db: Session, limit: int = 50) -> list[dict]:
    missions = (
        db.query(Mission).order_by(Mission.created_at.desc()).limit(limit).all()
    )
    return [serialize_mission(m, detail=False) for m in missions]


def get_mission(db: Session, mission_id: str) -> Mission | None:
    return db.get(Mission, mission_id)


def agent_stats(db: Session) -> dict:
    rows = (
        db.query(
            AgentResult.agent_name,
            func.count(AgentResult.id),
            func.max(AgentResult.created_at),
        )
        .group_by(AgentResult.agent_name)
        .all()
    )
    return {
        name: {"runs": count, "last_run": last}
        for name, count, last in rows
    }


def recent_activity(db: Session, limit: int = 50) -> list[dict]:
    activities = (
        db.query(Activity)
        .order_by(Activity.created_at.desc())
        .limit(limit)
        .all()
    )
    return [serialize_activity(a) for a in activities]
