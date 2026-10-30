"""Credix Backend — PredictionRecord ORM Model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class PredictionRecord(Base):
    """PredictionRecord table persisting verified model predictions and input snapshots."""

    __tablename__ = "prediction_records"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    model_version = Column(String(50), nullable=False, default="1.0.0")
    outcome = Column(String(50), nullable=False)  # "Approved" or "Rejected"
    probability = Column(Float, nullable=True)

    # Structured JSON for TreeSHAP factors and the 9-feature input snapshot
    explanation = Column(JSON, nullable=False)
    input_snapshot = Column(JSON, nullable=False)
    request_id = Column(String(100), nullable=True, index=True)

    # Relationships
    user = relationship("User", back_populates="predictions")

    # Composite index for fast paginated per-user history lookups
    __table_args__ = (
        Index("ix_prediction_records_user_created", "user_id", "created_at"),
    )

