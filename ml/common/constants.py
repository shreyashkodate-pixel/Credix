"""Credix ML Subsystem — Shared Constants & Schema Definitions.

Permanently codifies the 9 approved model features, excluded demographic
attributes (Fair Lending policy D-023), and target label mappings.
"""

from pathlib import Path

# Paths
ML_ROOT = Path(__file__).resolve().parent.parent
TRAINING_DATA_RAW = ML_ROOT / "training" / "data" / "raw" / "train.csv"
ARTIFACTS_DIR = ML_ROOT / "inference" / "artifacts"
MODEL_ARTIFACT_PATH = ARTIFACTS_DIR / "model.joblib"
METADATA_ARTIFACT_PATH = ARTIFACTS_DIR / "metadata.json"

# Target variable definition
TARGET_COLUMN = "loan_status"
RAW_TARGET_COLUMN = "Loan_Status"
TARGET_MAPPING = {"Y": 1, "N": 0}
INVERSE_TARGET_MAPPING = {1: "Approved", 0: "Rejected"}

# Fair Lending policy (D-023) - strictly excluded from all training & inference
EXCLUDED_COLUMNS = ["Loan_ID", "Gender", "Married"]

# Raw-to-standard feature name mapping
RAW_TO_STANDARD_COLUMN_MAP = {
    "ApplicantIncome": "applicant_income",
    "CoapplicantIncome": "coapplicant_income",
    "LoanAmount": "loan_amount",
    "Loan_Amount_Term": "loan_amount_term",
    "Credit_History": "credit_history",
    "Education": "education",
    "Self_Employed": "self_employed",
    "Dependents": "dependents",
    "Property_Area": "property_area",
    "Loan_Status": "loan_status",
}

# The 9 audited model features
NUMERICAL_FEATURES = [
    "applicant_income",
    "coapplicant_income",
    "loan_amount",
    "loan_amount_term",
]

CATEGORICAL_FEATURES = [
    "credit_history",
    "education",
    "self_employed",
    "dependents",
    "property_area",
]

FEATURE_COLUMNS = NUMERICAL_FEATURES + CATEGORICAL_FEATURES

# Categorical allowed values (validation boundaries)
ALLOWED_CATEGORICAL_VALUES = {
    "education": ["Graduate", "Not Graduate"],
    "self_employed": ["Yes", "No"],
    "dependents": ["0", "1", "2", "3+"],
    "property_area": ["Urban", "Semiurban", "Rural"],
    "credit_history": [0, 1],
}

# Allowed standard loan terms (months)
ALLOWED_LOAN_TERMS = [12, 36, 60, 120, 180, 240, 300, 360, 480]

# Model versioning baseline
MODEL_VERSION = "1.0.0"

