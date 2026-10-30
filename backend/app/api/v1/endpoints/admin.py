"""Credix Backend — Administrative Endpoints."""

from typing import Any, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.api.deps import get_current_admin
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.prediction import PredictionRecord
from backend.app.schemas.auth import UserResponse
from backend.app.services.audit_service import record_audit_event

router = APIRouter()


class AdminDashboardMetrics(BaseModel):
    """Aggregate statistics for admin dashboard (FR-022)."""
    total_users: int
    total_predictions: int
    approved_predictions: int
    rejected_predictions: int
    approval_rate_percent: float


class AdminUserListPage(BaseModel):
    """Paginated user list for admin review."""
    users: List[UserResponse]
    total: int
    page: int
    page_size: int


@router.get("/dashboard", response_model=AdminDashboardMetrics)
def get_admin_dashboard(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> Any:
    """Returns system-wide aggregate statistics. Restricted strictly to admin role."""
    record_audit_event(
        db=db,
        event_type="ADMIN_DASHBOARD_ACCESS",
        actor_user_id=admin.id,
        target_type="admin_dashboard",
        metadata={"role": admin.role},
    )
    db.commit()

    total_users = db.query(User).count()
    total_predictions = db.query(PredictionRecord).count()
    approved = (
        db.query(PredictionRecord)
        .filter(PredictionRecord.outcome == "Approved")
        .count()
    )
    rejected = (
        db.query(PredictionRecord)
        .filter(PredictionRecord.outcome == "Rejected")
        .count()
    )

    approval_rate = (
        round((approved / total_predictions) * 100, 2)
        if total_predictions > 0
        else 0.0
    )

    return AdminDashboardMetrics(
        total_users=total_users,
        total_predictions=total_predictions,
        approved_predictions=approved,
        rejected_predictions=rejected,
        approval_rate_percent=approval_rate,
    )


@router.get("/users", response_model=AdminUserListPage)
def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> Any:
    """Returns bounded paginated list of registered users. Restricted to admin."""
    record_audit_event(
        db=db,
        event_type="ADMIN_USERS_LIST_ACCESS",
        actor_user_id=admin.id,
        target_type="user_list",
        metadata={"page": page, "page_size": page_size},
    )
    db.commit()

    offset = (page - 1) * page_size
    query = db.query(User)
    total = query.count()
    users = query.order_by(User.created_at.desc()).offset(offset).limit(page_size).all()

    return AdminUserListPage(
        users=users,
        total=total,
        page=page,
        page_size=page_size,
    )

