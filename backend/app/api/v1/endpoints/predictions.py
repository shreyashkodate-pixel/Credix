"""Credix Backend — Prediction and History Endpoints."""

import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.prediction import PredictionRecord
from backend.app.schemas.prediction import (
    PredictionCreateRequest,
    PredictionResponse,
    PredictionHistoryPage,
    PredictionHistoryItem,
)
from backend.app.services.ml_service import MLOrchestrator

router = APIRouter()


@router.post("", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
def create_prediction(
    prediction_in: PredictionCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Submits 9-feature applicant data, runs ML inference, and atomically saves the result.
    
    Enforces D-016: Prediction is linked directly to the authenticated identity.
    Enforces FR-014: Failed inference cannot be saved as successful.
    Enforces Finding 1: Persists trusted server-side request_id for end-to-end correlation.
    """
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    result = MLOrchestrator.run_prediction_and_persist(
        request_data=prediction_in,
        user_id=current_user.id,
        db=db,
        request_id=request_id,
    )
    return result


@router.get("/history", response_model=PredictionHistoryPage)
def get_prediction_history(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page (max 100)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieves paginated personal prediction history owned by the caller.
    
    Enforces FR-018 & FR-020: Users can ONLY see their own historical records.
    """
    offset = (page - 1) * page_size
    query = db.query(PredictionRecord).filter(PredictionRecord.user_id == current_user.id)

    total = query.count()
    records = (
        query.order_by(PredictionRecord.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return PredictionHistoryPage(
        items=records,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/history/{prediction_id}", response_model=PredictionHistoryItem)
def get_prediction_detail(
    prediction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieves a single owned prediction record by ID.
    
    Enforces FR-018: Returns 404 if record does not belong to the authenticated user.
    """
    record = (
        db.query(PredictionRecord)
        .filter(
            PredictionRecord.id == prediction_id,
            PredictionRecord.user_id == current_user.id,
        )
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction record not found.",
        )
    return record

