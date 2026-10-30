"""Credix Backend — Health & Liveness Endpoints."""

from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.core.config import settings
from backend.app.core.database import get_db
from ml.inference.model.loader import ModelLoader

router = APIRouter()


class HealthCheckResponse(BaseModel):
    status: str
    environment: str
    database: str
    ml_model_ready: bool
    model_version: str


@router.get("/health", response_model=HealthCheckResponse)
def health_check(db: Session = Depends(get_db)) -> Any:
    """System liveness and readiness check (FR-027)."""
    # Check DB vitality
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # Check ML subsystem readiness
    ml_ready = ModelLoader.is_ready()
    meta = ModelLoader.get_metadata()

    return HealthCheckResponse(
        status="ok" if db_status == "connected" and ml_ready else "degraded",
        environment=settings.ENVIRONMENT,
        database=db_status,
        ml_model_ready=ml_ready,
        model_version=meta.get("model_version", "1.0.0"),
    )

