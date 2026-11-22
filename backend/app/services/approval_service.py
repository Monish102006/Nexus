"""Approval workflow — the only path to an outbound external action."""

import logging

from sqlalchemy.orm import Session

from ..config import settings
from ..models import Activity, Approval, Mission, utcnow
from ..services.mission_service import serialize_approval
from ..services.telegram_chats import latest_known_chat_id

logger = logging.getLogger("nexus.approvals")


class ApprovalError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def list_approvals(db: Session, status: str | None = None) -> list[dict]:
    query = db.query(Approval).order_by(Approval.created_at.desc())
    if status:
        query = query.filter(Approval.status == status)
    return [serialize_approval(a) for a in query.all()]


def _log(db, approval, activity_type, message, level="info"):
    db.add(
        Activity(
            mission_id=approval.mission_id,
            type=activity_type,
            message=message,
            level=level,
        )
    )
    db.commit()


async def approve(db: Session, approval_id: str) -> dict:
    approval = db.get(Approval, approval_id)
    if approval is None:
        raise ApprovalError("Approval not found", 404)

    # Duplicate-send prevention: only a pending action can be approved once.
    if approval.status != "pending":
        raise ApprovalError(
            f"Approval is already '{approval.status}' and cannot be approved again.",
            409,
        )

    mission = db.get(Mission, approval.mission_id)
    approval.status = "approved"
    approval.decided_at = utcnow()
    approval.send_attempted = True
    approval.execution_note = "Approved by human operator."
    if mission:
        mission.status = "approved"
        mission.updated_at = utcnow()
    db.commit()
    _log(
        db,
        approval,
        "approval_approved",
        "Human approved the Telegram announcement.",
        "success",
    )

    from ..integrations.telegram_bot import telegram_manager

    if not telegram_manager.running:
        approval.execution_note = (
            "Action approved but not delivered: Telegram bot is not running "
            "or credentials are missing."
        )
        db.commit()
        _log(
            db,
            approval,
            "telegram_not_configured",
            "Telegram delivery skipped — bot not configured or not running.",
            "warning",
        )
        return serialize_approval(approval)

    chat_id = approval.target_chat_id or (
        str(settings.telegram_default_chat_id)
        if settings.telegram_default_chat_id is not None
        else None
    )
    if not chat_id:
        chat_id = latest_known_chat_id(db)
    if not chat_id:
        approval.execution_note = (
            "Action approved but not delivered: no target Telegram chat is known."
        )
        db.commit()
        _log(
            db,
            approval,
            "telegram_not_configured",
            "Telegram delivery skipped — no target chat configured.",
            "warning",
        )
        return serialize_approval(approval)

    try:
        message_id = await telegram_manager.send_message(
            approval.content, int(chat_id)
        )
    except Exception as exc:  # noqa: BLE001 - record failure honestly
        logger.exception("Telegram delivery failed")
        approval.status = "failed"
        approval.execution_note = f"Telegram delivery failed: {exc}"
        if mission:
            mission.status = "failed"
            mission.error = approval.execution_note[:500]
            mission.updated_at = utcnow()
        db.commit()
        _log(
            db,
            approval,
            "telegram_failed",
            f"Telegram delivery failed: {exc}",
            "error",
        )
        return serialize_approval(approval)

    approval.status = "sent"
    approval.telegram_message_id = message_id
    approval.executed_at = utcnow()
    approval.execution_note = "Delivered to Telegram."
    if mission:
        mission.status = "completed"
        mission.updated_at = utcnow()
    db.commit()
    _log(
        db,
        approval,
        "telegram_sent",
        f"Announcement delivered to Telegram (message {message_id}).",
        "success",
    )
    if mission:
        _log(db, approval, "mission_completed", "Mission completed.", "success")
    return serialize_approval(approval)


def reject(db: Session, approval_id: str) -> dict:
    approval = db.get(Approval, approval_id)
    if approval is None:
        raise ApprovalError("Approval not found", 404)
    if approval.status != "pending":
        raise ApprovalError(
            f"Approval is already '{approval.status}' and cannot be rejected.",
            409,
        )

    mission = db.get(Mission, approval.mission_id)
    approval.status = "rejected"
    approval.decided_at = utcnow()
    approval.execution_note = "Rejected by human operator. No message was sent."
    if mission:
        mission.status = "rejected"
        mission.updated_at = utcnow()
    db.commit()
    _log(
        db,
        approval,
        "approval_rejected",
        "Human rejected the Telegram announcement. Nothing was sent.",
        "warning",
    )
    return serialize_approval(approval)
