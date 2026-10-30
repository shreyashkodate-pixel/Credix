"""Credix ML — Core Predictor with TreeSHAP Explanations.

Executes inference using the fitted champion pipeline and extracts local
TreeSHAP feature attributions to explain each loan decision.
"""

import os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

from typing import Dict, Any, List
import numpy as np
import pandas as pd
import shap

from ml.common.constants import INVERSE_TARGET_MAPPING
from ml.common.utils import setup_logger
from ml.inference.model.loader import ModelLoader

logger = setup_logger("predictor")

FRIENDLY_FEATURE_MAP = {
    "credit_history_1": "Positive Credit History",
    "credit_history_0": "Delinquent or Absent Credit History",
    "education_Graduate": "Higher Education (Graduate)",
    "education_Not Graduate": "Non-Graduate Education",
    "property_area_Semiurban": "Semiurban Property Location",
    "property_area_Rural": "Rural Property Location",
    "property_area_Urban": "Urban Property Location",
    "self_employed_Yes": "Self-Employment Status",
    "self_employed_No": "Standard Employment Status",
    "dependents_0": "No Dependent Financial Burden",
    "dependents_1": "1 Dependent",
    "dependents_2": "2 Dependents",
    "dependents_3+": "3+ Dependents",
    "applicant_income": "Applicant Monthly Income",
    "coapplicant_income": "Co-applicant Income",
    "loan_amount": "Loan Amount Requested",
    "loan_amount_term": "Loan Repayment Term",
}


class Predictor:
    """Inference engine with integrated SHAP explainability."""

    _explainer = None

    def __init__(self):
        self.pipeline, self.metadata = ModelLoader.load()
        self.preprocessor = self.pipeline.named_steps["preprocessor"]
        self.classifier = self.pipeline.named_steps["classifier"]
        self._init_explainer()

    def _init_explainer(self):
        """Initializes the TreeExplainer once."""
        if Predictor._explainer is None:
            try:
                logger.info("Initializing TreeSHAP explainer for champion model...")
                Predictor._explainer = shap.TreeExplainer(self.classifier)
                logger.info("TreeSHAP explainer ready.")
            except Exception as e:
                logger.warning(f"Could not initialize TreeSHAP explainer: {e}")
                Predictor._explainer = None

    def predict(self, input_df: pd.DataFrame) -> Dict[str, Any]:
        """Runs model prediction and generates explanatory factors.
        
        Returns:
            Dict containing outcome, probability, model_version, and explanation.
        """
        # 1. Model inference
        raw_pred = int(self.pipeline.predict(input_df)[0])
        probabilities = self.pipeline.predict_proba(input_df)[0]
        approval_prob = float(probabilities[1])
        outcome = INVERSE_TARGET_MAPPING.get(raw_pred, "Unknown")

        # 2. Extract SHAP Explanations
        factors = self._generate_shap_factors(input_df)

        return {
            "outcome": outcome,
            "raw_class": raw_pred,
            "probability": round(approval_prob, 4),
            "model_version": self.metadata.get("model_version", "1.0.0"),
            "algorithm": self.metadata.get("champion_algorithm", "RandomForest"),
            "explanation": {
                "method": "TreeSHAP",
                "factors": factors,
            },
        }

    def _generate_shap_factors(self, input_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Computes top contributing features for the prediction."""
        if Predictor._explainer is None:
            return []

        try:
            # Transform input using the pipeline preprocessor
            X_trans = self.preprocessor.transform(input_df)
            raw_feature_names = self.preprocessor.get_feature_names_out()

            # Compute SHAP values for class 1 (Approval)
            shap_values = Predictor._explainer.shap_values(X_trans)

            # In scikit-learn binary classification, shap_values can be a list of [neg, pos] or 2D array
            if isinstance(shap_values, list):
                pos_shaps = shap_values[1][0]
            elif len(shap_values.shape) == 3:
                pos_shaps = shap_values[0, :, 1]
            else:
                pos_shaps = shap_values[0]

            # Pair features with their attribution
            attributions = []
            for raw_name, val in zip(raw_feature_names, pos_shaps):
                clean_key = raw_name.replace("num__", "").replace("cat__", "")
                friendly_name = FRIENDLY_FEATURE_MAP.get(clean_key, clean_key.replace("_", " ").title())
                
                attributions.append({
                    "raw_key": clean_key,
                    "feature": friendly_name,
                    "attribution": float(val),
                    "impact": "positive" if val > 0 else "negative",
                })

            # Sort by absolute attribution magnitude
            attributions.sort(key=lambda x: abs(x["attribution"]), reverse=True)

            # Take top 4 most impactful factors
            top_factors = []
            for item in attributions[:4]:
                top_factors.append({
                    "factor": item["feature"],
                    "impact": item["impact"],
                    "weight": round(abs(item["attribution"]), 4),
                    "description": self._describe_factor(item["feature"], item["impact"]),
                })
            return top_factors
        except Exception as e:
            logger.warning(f"Failed to generate SHAP factors: {e}")
            return []

    def _describe_factor(self, factor_name: str, impact: str) -> str:
        """Generates clear, non-causal user-facing explanations."""
        if impact == "positive":
            return f"{factor_name} contributed positively toward approval."
        else:
            return f"{factor_name} contributed negatively toward approval."
