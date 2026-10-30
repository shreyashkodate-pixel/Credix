"""Credix ML Inference Service Configuration Settings."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"

MODEL_PATH = Path(os.getenv("MODEL_PATH", str(ARTIFACTS_DIR / "model.joblib")))
METADATA_PATH = Path(os.getenv("METADATA_PATH", str(ARTIFACTS_DIR / "metadata.json")))

SERVICE_HOST = os.getenv("ML_SERVICE_HOST", "0.0.0.0")
SERVICE_PORT = int(os.getenv("ML_SERVICE_PORT", "8001"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

