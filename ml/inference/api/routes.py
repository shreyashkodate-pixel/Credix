"""FastAPI router and application factory for Credix ML inference service."""

from fastapi import APIRouter, HTTPException, status
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ml.inference.api.schema import PredictionRequest, PredictionResponse, HealthResponse
from ml.inference.model.loader import ModelLoader
from ml.inference.services.prediction_service import PredictionService
from ml.inference.preprocessing.preprocess import InputValidationError

router = APIRouter()
_service = None


def get_prediction_service() -> PredictionService:
    global _service
    if _service is None:
        _service = PredictionService()
    return _service


@router.get("/health", response_model=HealthResponse)
def health():
    """Liveness probe."""
    ready = ModelLoader.is_ready()
    metadata = ModelLoader.get_metadata()
    return HealthResponse(
        status="ok",
        model_ready=ready,
        model_version=metadata.get("model_version"),
    )


@router.get("/ready", response_model=HealthResponse)
def ready():
    """Readiness probe."""
    if not ModelLoader.is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model artifacts are not loaded or invalid",
        )
    metadata = ModelLoader.get_metadata()
    return HealthResponse(
        status="ok",
        model_ready=True,
        model_version=metadata.get("model_version"),
    )


@router.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    """Executes loan approval prediction with TreeSHAP explanations."""
    try:
        service = get_prediction_service()
        payload = request.model_dump()
        result = service.predict(payload)
        return result
    except InputValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference failure: {str(e)}",
        )


def create_app() -> FastAPI:
    """Builds and returns the standalone ML Inference FastAPI application."""
    app = FastAPI(
        title="Credix ML Inference Service",
        version="1.0.0",
        description="Stateless loan approval prediction and TreeSHAP explanation service",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    return app

