"""Credix ML — Core Pipeline Construction.

Constructs the reproducible ColumnTransformer and Pipeline objects used
identically across training and inference to avoid training-serving skew.
"""

from typing import Tuple, Optional
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

from ml.common.constants import (
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    RAW_TO_STANDARD_COLUMN_MAP,
    EXCLUDED_COLUMNS,
    TARGET_MAPPING,
)


def build_preprocessor() -> ColumnTransformer:
    """Builds the feature preprocessing ColumnTransformer.
    
    Transforms:
    - Numerical features: Median imputation + Standard scaling.
    - Categorical features: Most frequent (mode) imputation + One-Hot Encoding.
    """
    numerical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numerical_transformer, NUMERICAL_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
        ],
        remainder="drop",  # Drops any extra columns not in the 9 audited features
    )
    return preprocessor


def build_full_pipeline(classifier) -> Pipeline:
    """Wraps the preprocessor and a candidate classifier into a single Pipeline."""
    preprocessor = build_preprocessor()
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )
    return pipeline


def prepare_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[pd.Series]]:
    """Cleans a DataFrame, standardizes columns, drops excluded attributes, and separates X and y.
    
    1. Renames raw columns to standard snake_case names.
    2. Drops Loan_ID, Gender, and Married (Fair Lending policy D-023).
    3. Converts data types appropriately.
    4. Extracts target variable if present.
    """
    data = df.copy()

    # Standardize column names if raw headers are present
    data = data.rename(columns=RAW_TO_STANDARD_COLUMN_MAP)

    # Drop explicitly excluded columns (Fair Lending compliance)
    for col in EXCLUDED_COLUMNS:
        standard_name = RAW_TO_STANDARD_COLUMN_MAP.get(col, col.lower())
        if standard_name in data.columns:
            data = data.drop(columns=[standard_name])
        if col in data.columns:
            data = data.drop(columns=[col])

    # Extract target if present
    y = None
    if TARGET_COLUMN in data.columns:
        # Convert Y/N string to 1/0 int if needed
        if data[TARGET_COLUMN].dtype == object or isinstance(data[TARGET_COLUMN].iloc[0], str):
            y = data[TARGET_COLUMN].map(TARGET_MAPPING).astype(int)
        else:
            y = data[TARGET_COLUMN].astype(int)
        data = data.drop(columns=[TARGET_COLUMN])

    # Retain strictly the 9 feature columns
    available_cols = [c for c in FEATURE_COLUMNS if c in data.columns]
    X = data[available_cols].copy()

    # Ensure numeric types
    for col in NUMERICAL_FEATURES:
        if col in X.columns:
            X[col] = pd.to_numeric(X[col], errors="coerce")

    # Standardize credit_history specifically to '0' and '1' strings
    if "credit_history" in X.columns:
        X["credit_history"] = X["credit_history"].apply(
            lambda v: str(int(float(v))) if pd.notnull(v) and str(v).strip() not in ("", "nan", "None") else None
        )

    # Ensure categorical types as strings for imputation
    for col in CATEGORICAL_FEATURES:
        if col != "credit_history" and col in X.columns:
            X[col] = X[col].astype(str).replace({"nan": None, "None": None})

    return X, y
