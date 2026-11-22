import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..integrations.telegram_bot import telegram_manager
from ..models import Mission
from ..schemas import MissionCreate
from ..services import approval_service, mission_service

logger = logging.getLogger("nexus.api")

router = APIRouter(prefix="/api")

AGENT_DEFINITIONS = [
    {
        "key": "research",
        "name": "Research Agent",
        "icon": "Search",
        "description": "Extracts requirements, constraints and missing information.",
        "capabilities": [
            "Requirement extraction",
            "Constraint analysis",
            "Gap detection",
            "Risk identification",
        ],
    },
    {
        "key": "planning",
        "name": "Planning Agent",
        "icon": "ListChecks",
        "description": "Generates tasks, priorities, deadlines and dependencies.",
        "capabilities": [
            "Task decomposition",
            "Priority assignment",
            "Deadline scheduling",
            "Dependency mapping",
        ],
    },
    {
        "key": "communication",
        "name": "Communication Agent",
        "icon": "Send",
        "description": "Drafts Telegram announcements and approval payloads.",
        "capabilities": [
            "Announcement drafting",
            "Tone control",
            "Action payloads",
            "Approval hand-off",
        ],
    },
]


@router.get("/health")
def health(db: Session = Depends(get_db)):
    from ..services.telegram_chats import known_chat_count

    return {
        "status": "ok",
        "app": settings.app_name,
        "mode": "demo" if settings.demo_mode else "live",
        "demo_mode": settings.demo_mode,
        "llm_configured": settings.llm_configured,
        "llm_model": settings.llm_model if settings.llm_configured else None,
        "telegram_configured": settings.telegram_configured,
        "telegram_running": telegram_manager.running,
        "telegram_error": telegram_manager.last_error,
        "telegram_known_chats": known_chat_count(db),
        "time": datetime.now(timezone.utc),
    }


@router.post("/missions", status_code=201)
async def create_mission(payload: MissionCreate, db: Session = Depends(get_db)):
    mission = mission_service.create_mission(
        db, payload.objective, source=payload.source or "web"
    )
    await mission_service.run_mission(db, mission)
    db.refresh(mission)
    return mission_service.serialize_mission(mission, detail=True)


@router.get("/missions")
def list_missions(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return mission_service.list_missions(db, limit=limit)


@router.get("/missions/{mission_id}")
def get_mission(mission_id: str, db: Session = Depends(get_db)):
    mission = mission_service.get_mission(db, mission_id)
    if mission is None:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission_service.serialize_mission(mission, detail=True)


@router.get("/agents")
def list_agents(db: Session = Depends(get_db)):
    stats = mission_service.agent_stats(db)
    agents = []
    for definition in AGENT_DEFINITIONS:
        info = dict(definition)
        stat = stats.get(definition["key"], {})
        info["runs"] = stat.get("runs", 0)
        info["last_run"] = stat.get("last_run")
        info["mode"] = "demo" if settings.demo_mode else "live"
        info["status"] = "ready"
        agents.append(info)
    return {
        "mode": "demo" if settings.demo_mode else "live",
        "agents": agents,
    }


@router.get("/approvals")
def list_approvals(
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return approval_service.list_approvals(db, status=status)


@router.post("/approvals/{approval_id}/approve")
async def approve(approval_id: str, db: Session = Depends(get_db)):
    try:
        return await approval_service.approve(db, approval_id)
    except approval_service.ApprovalError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.post("/approvals/{approval_id}/reject")
def reject(approval_id: str, db: Session = Depends(get_db)):
    try:
        return approval_service.reject(db, approval_id)
    except approval_service.ApprovalError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.get("/activity")
def list_activity(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return mission_service.recent_activity(db, limit=limit)
