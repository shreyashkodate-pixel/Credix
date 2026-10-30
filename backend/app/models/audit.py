"""Credix Backend — AuditEvent ORM Model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON

from backend.app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class AuditEvent(Base):
    """AuditEvent table logging administrative events and security actions."""

    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    actor_user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    event_type = Column(String(100), nullable=False, index=True)
    target_type = Column(String(100), nullable=True)
    target_id = Column(String(100), nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

