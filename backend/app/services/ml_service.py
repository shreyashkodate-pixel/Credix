"""Credix Backend — ML Orchestration and Atomic Persistence Service."""

import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.app.models.prediction import PredictionRecord
from backend.app.schemas.prediction import PredictionCreateRequest, PredictionResponse
from ml.inference.services.prediction_service import PredictionService
from ml.inference.model.loader import ModelLoader

logger = logging.getLogger("backend.ml_service")
_prediction_service = None


def get_prediction_service() -> PredictionService:
    """Singleton getter for the ML PredictionService."""
    global _prediction_service
    if _prediction_service is None:
        if not ModelLoader.is_ready():
            logger.error("ML model artifacts are not ready or missing.")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ML model artifacts are currently unavailable.",
            )
        _prediction_service = PredictionService()
    return _prediction_service


class MLOrchestrator:
    """Coordinates prediction execution and atomic database persistence."""

    @staticmethod
    def run_prediction_and_persist(
        request_data: PredictionCreateRequest,
        user_id: str,
        db: Session,
        request_id: str = None,
    ) -> PredictionResponse:
        """Executes inference and atomically saves the result to PostgreSQL.
        
        Enforces SRS FR-014: If inference fails, no successful record is saved.
        """
        service = get_prediction_service()
        input_dict = request_data.model_dump()

        try:
            # 1. Execute ML Inference + TreeSHAP explainability
            inference_result = service.predict(input_dict)
        except Exception as e:
            logger.error(f"Inference execution failed for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Prediction model execution failed.",
            )

        # 2. Atomically persist to database
        try:
            record = PredictionRecord(
                user_id=user_id,
                model_version=inference_result["model_version"],
                outcome=inference_result["outcome"],
                probability=inference_result.get("probability"),
                explanation=inference_result["explanation"],
                input_snapshot=input_dict,
                request_id=request_id,
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            logger.info(f"Successfully persisted prediction {record.id} for user {user_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Database persistence failed for prediction: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to persist prediction record to database.",
            )

        # 3. Format and return API response
        return PredictionResponse(
            prediction_id=record.id,
            outcome=record.outcome,
            probability=record.probability,
            model_version=record.model_version,
            created_at=record.created_at,
            explanation=record.explanation,
        )

