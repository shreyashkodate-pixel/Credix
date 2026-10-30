"""Credix ML — Inference-Time Input Preprocessing & Validation.

Ensures incoming inference dictionaries adhere strictly to the 9-feature
schema before passing to the pipeline. Rejects prohibited demographics.
"""

from typing import Dict, Any, Tuple
import pandas as pd

from ml.common.constants import (
    FEATURE_COLUMNS,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    ALLOWED_CATEGORICAL_VALUES,
    ALLOWED_LOAN_TERMS,
    EXCLUDED_COLUMNS,
)


class InputValidationError(ValueError):
    """Raised when an applicant payload fails contract validation."""
    pass


def validate_and_format_input(payload: Dict[str, Any]) -> pd.DataFrame:
    """Validates raw applicant dictionary and returns a 1-row DataFrame.
    
    Raises InputValidationError if required fields are missing, out of range,
    or contain prohibited demographic attributes (Fair Lending policy D-023).
    """
    # 1. Reject prohibited demographic keys
    for excluded in EXCLUDED_COLUMNS:
        if excluded in payload or excluded.lower() in payload:
            raise InputValidationError(
                f"Prohibited demographic field '{excluded}' detected. "
                "Fair Lending policy strictly excludes demographic data from inference."
            )

    # 2. Check for missing required features
    missing = [f for f in FEATURE_COLUMNS if f not in payload]
    if missing:
        raise InputValidationError(f"Missing required prediction features: {missing}")

    # 3. Validate numerical bounds
    try:
        app_income = float(payload["applicant_income"])
        if app_income <= 0:
            raise InputValidationError("applicant_income must be greater than 0")

        coapp_income = float(payload.get("coapplicant_income", 0.0))
        if coapp_income < 0:
            raise InputValidationError("coapplicant_income must be greater than or equal to 0")

        loan_amount = float(payload["loan_amount"])
        if loan_amount <= 0:
            raise InputValidationError("loan_amount must be greater than 0")

        loan_term = int(payload["loan_amount_term"])
        if loan_term not in ALLOWED_LOAN_TERMS:
            raise InputValidationError(
                f"loan_amount_term must be one of {ALLOWED_LOAN_TERMS}, got {loan_term}"
            )
    except (ValueError, TypeError) as e:
        raise InputValidationError(f"Invalid numerical value: {e}")

    # 4. Validate categorical enums
    for cat_col, allowed in ALLOWED_CATEGORICAL_VALUES.items():
        val = payload[cat_col]
        if cat_col == "credit_history":
            try:
                val = int(val)
            except (ValueError, TypeError):
                raise InputValidationError("credit_history must be 1 or 0")
        if val not in allowed:
            raise InputValidationError(
                f"Invalid value for '{cat_col}': '{val}'. Allowed values: {allowed}"
            )

    # 5. Build clean single-row DataFrame
    row_data = {
        "applicant_income": [app_income],
        "coapplicant_income": [coapp_income],
        "loan_amount": [loan_amount],
        "loan_amount_term": [loan_term],
        "credit_history": [str(payload["credit_history"])],
        "education": [str(payload["education"])],
        "self_employed": [str(payload["self_employed"])],
        "dependents": [str(payload["dependents"])],
        "property_area": [str(payload["property_area"])],
    }
    df = pd.DataFrame(row_data)
    return df

