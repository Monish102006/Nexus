import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


def uid() -> str:
    return uuid.uuid4().hex


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Mission(Base):
    __tablename__ = "missions"

    id = Column(String, primary_key=True, default=uid)
    objective = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="running")
    summary = Column(Text, nullable=True)
    source = Column(String, nullable=False, default="web")
    source_chat_id = Column(String, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    tasks = relationship(
        "Task", back_populates="mission", cascade="all, delete-orphan",
        order_by="Task.order_index",
    )
    agent_results = relationship(
        "AgentResult", back_populates="mission", cascade="all, delete-orphan",
        order_by="AgentResult.created_at",
    )
    approvals = relationship(
        "Approval", back_populates="mission", cascade="all, delete-orphan",
        order_by="Approval.created_at",
    )
    activities = relationship(
        "Activity", back_populates="mission", cascade="all, delete-orphan",
        order_by="Activity.created_at",
    )


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=uid)
    mission_id = Column(String, ForeignKey("missions.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String, nullable=False, default="medium")
    deadline = Column(String, nullable=True)
    dependency = Column(String, nullable=True)
    status = Column(String, nullable=False, default="pending")
    order_index = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    mission = relationship("Mission", back_populates="tasks")


class AgentResult(Base):
    __tablename__ = "agent_results"

    id = Column(String, primary_key=True, default=uid)
    mission_id = Column(String, ForeignKey("missions.id"), nullable=False, index=True)
    agent_name = Column(String, nullable=False)
    role = Column(String, nullable=True)
    status = Column(String, nullable=False, default="completed")
    source = Column(String, nullable=False, default="demo")
    output = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    mission = relationship("Mission", back_populates="agent_results")


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(String, primary_key=True, default=uid)
    mission_id = Column(String, ForeignKey("missions.id"), nullable=False, index=True)
    action_type = Column(String, nullable=False, default="telegram_send")
    channel = Column(String, nullable=False, default="telegram")
    content = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="pending")
    target_chat_id = Column(String, nullable=True)
    telegram_message_id = Column(String, nullable=True)
    execution_note = Column(Text, nullable=True)
    send_attempted = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    decided_at = Column(DateTime(timezone=True), nullable=True)
    executed_at = Column(DateTime(timezone=True), nullable=True)

    mission = relationship("Mission", back_populates="approvals")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(String, primary_key=True, default=uid)
    mission_id = Column(String, ForeignKey("missions.id"), nullable=True, index=True)
    type = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    level = Column(String, nullable=False, default="info")
    created_at = Column(DateTime(timezone=True), default=utcnow)

    mission = relationship("Mission", back_populates="activities")


class TelegramChat(Base):
    """Chats that have interacted with the bot (used as a delivery fallback)."""

    __tablename__ = "telegram_chats"

    chat_id = Column(String, primary_key=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    last_seen = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

