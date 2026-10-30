"""Credix Backend — Unified API v1 Router."""

from fastapi import APIRouter

from backend.app.api.v1.endpoints import auth, predictions, admin, health

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(health.router, tags=["health"])

