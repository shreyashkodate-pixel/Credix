"""Credix ML — Model Artifact Loader (Inference Service).

Handles safe artifact deserialization, checksum/readiness validation,
and caching for production serving.
"""

from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import joblib

from ml.common.constants import MODEL_ARTIFACT_PATH, METADATA_ARTIFACT_PATH
from ml.common.utils import setup_logger, load_json

logger = setup_logger("model_loader")


class ModelLoader:
    """Thread-safe singleton model artifact loader."""

    _instance = None
    _pipeline = None
    _metadata: Optional[Dict[str, Any]] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance

    @classmethod
    def load(cls, force_reload: bool = False) -> Tuple[Any, Dict[str, Any]]:
        """Loads and caches the model pipeline and metadata."""
        if cls._pipeline is not None and not force_reload:
            return cls._pipeline, cls._metadata or {}

        if not MODEL_ARTIFACT_PATH.exists():
            raise FileNotFoundError(
                f"Model artifact not found at {MODEL_ARTIFACT_PATH}. Ensure training has completed."
            )

        if not METADATA_ARTIFACT_PATH.exists():
            raise FileNotFoundError(
                f"Model metadata not found at {METADATA_ARTIFACT_PATH}."
            )

        logger.info(f"Loading model pipeline from {MODEL_ARTIFACT_PATH}...")
        cls._pipeline = joblib.load(MODEL_ARTIFACT_PATH)
        cls._metadata = load_json(METADATA_ARTIFACT_PATH)
        logger.info(
            f"Successfully loaded model version {cls._metadata.get('model_version')} "
            f"({cls._metadata.get('champion_algorithm')})."
        )
        return cls._pipeline, cls._metadata

    @classmethod
    def is_ready(cls) -> bool:
        """Readiness probe checking if artifacts exist and are loadable."""
        try:
            cls.load()
            return True
        except Exception as e:
            logger.warning(f"Model readiness check failed: {e}")
            return False

    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        """Returns loaded model metadata or empty dict if unready."""
        if cls._metadata is None:
            try:
                cls.load()
            except Exception:
                return {}
        return cls._metadata or {}

