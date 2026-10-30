"""Credix ML — High-Level Prediction Service Entrypoint.

Main orchestration service that receives applicant payloads, executes
validation, runs the predictor, and packages the result for downstream consumers.
"""

from typing import Dict, Any

from ml.common.utils import setup_logger
from ml.inference.preprocessing.preprocess import validate_and_format_input, InputValidationError
from ml.inference.model.predictor import Predictor

logger = setup_logger("prediction_service")


class PredictionService:
    """Service layer coordinating input validation, ML inference, and explanation."""

    def __init__(self):
        self.predictor = Predictor()

    def predict(self, applicant_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validates payload and returns model prediction with explanations.
        
        Raises InputValidationError on malformed payloads or demographic keys.
        """
        # 1. Validate and convert dictionary to DataFrame
        formatted_df = validate_and_format_input(applicant_payload)

        # 2. Execute inference and explanation
        result = self.predictor.predict(formatted_df)

        return result

