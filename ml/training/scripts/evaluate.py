"""Credix ML — Model Evaluation and Calibration Assessment Script.

Generates comprehensive evaluation metrics, confusion matrix, and probability
calibration curve diagnostics for the champion model.
"""

import sys
from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
)
from sklearn.calibration import calibration_curve

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.common.constants import TRAINING_DATA_RAW, MODEL_ARTIFACT_PATH
from ml.common.utils import setup_logger
from ml.pipeline.pipeline import prepare_data

logger = setup_logger("evaluate")


def run_evaluation():
    logger.info("Running evaluation on full training dataset...")
    if not MODEL_ARTIFACT_PATH.exists():
        raise FileNotFoundError(f"Model artifact not found at {MODEL_ARTIFACT_PATH}")

    pipeline = joblib.load(MODEL_ARTIFACT_PATH)
    raw_df = pd.read_csv(TRAINING_DATA_RAW)
    X, y = prepare_data(raw_df)

    y_pred = pipeline.predict(X)
    y_prob = pipeline.predict_proba(X)[:, 1]

    # Overall Metrics
    roc_auc = roc_auc_score(y, y_prob)
    pr_auc = average_precision_score(y, y_prob)
    brier = brier_score_loss(y, y_prob)

    print("\n" + "=" * 60)
    print("           CREDIX MODEL EVALUATION REPORT")
    print("=" * 60)
    print(f"Total Evaluated Samples: {len(X)}")
    print(f"ROC-AUC Score:           {roc_auc:.4f}")
    print(f"PR-AUC Score:            {pr_auc:.4f}")
    print(f"Brier Score (Loss):      {brier:.4f} (lower is better, <0.20 is good)")
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y, y_pred)
    print(f"  [TN: {cm[0,0]:3d}  |  FP: {cm[0,1]:3d}]  (Rejected: 0)")
    print(f"  [FN: {cm[1,0]:3d}  |  TP: {cm[1,1]:3d}]  (Approved: 1)")

    print("\nClassification Report:")
    print(classification_report(y, y_pred, target_names=["Rejected (0)", "Approved (1)"]))

    # Calibration Curve Analysis
    prob_true, prob_pred = calibration_curve(y, y_prob, n_bins=5)
    print("Probability Calibration Bins (Mean Predicted Prob vs True Fraction):")
    for pred, true in zip(prob_pred, prob_true):
        print(f"  Predicted: {pred:6.2f}  ==>  Actual True: {true:6.2f}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_evaluation()

