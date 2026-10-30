"""Credix ML — Offline Model Training and Benchmarking Entrypoint.

Trains and compares baseline and ensemble models using 5-Fold Stratified
Cross-Validation. Selects the best performing model, fits on the complete
dataset, and serializes the champion pipeline to ml/inference/artifacts/.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
    accuracy_score,
    roc_auc_score,
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    brier_score_loss,
)

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.common.constants import (
    TRAINING_DATA_RAW,
    MODEL_ARTIFACT_PATH,
    METADATA_ARTIFACT_PATH,
    MODEL_VERSION,
    FEATURE_COLUMNS,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
)
from ml.common.utils import setup_logger, save_json
from ml.pipeline.pipeline import build_full_pipeline, prepare_data

logger = setup_logger("train")


def evaluate_cv(pipeline_builder, model_factory, X, y, cv=5):
    """Runs Stratified K-Fold Cross Validation and computes robust metrics."""
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)

    metrics = {
        "accuracy": [],
        "roc_auc": [],
        "pr_auc": [],
        "f1_macro": [],
        "f1_rejected": [],  # Minority class (0)
        "precision_rejected": [],
        "recall_rejected": [],
        "brier_score": [],
    }

    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y), 1):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        model = model_factory()
        pipeline = pipeline_builder(model)
        pipeline.fit(X_train, y_train)

        # Predictions and probabilities
        y_pred = pipeline.predict(X_val)
        y_prob = pipeline.predict_proba(X_val)[:, 1]

        # Compute fold metrics
        metrics["accuracy"].append(accuracy_score(y_val, y_pred))
        metrics["roc_auc"].append(roc_auc_score(y_val, y_prob))
        metrics["pr_auc"].append(average_precision_score(y_val, y_prob))
        metrics["f1_macro"].append(f1_score(y_val, y_pred, average="macro"))
        metrics["f1_rejected"].append(f1_score(y_val, y_pred, pos_label=0, zero_division=0))
        metrics["precision_rejected"].append(precision_score(y_val, y_pred, pos_label=0, zero_division=0))
        metrics["recall_rejected"].append(recall_score(y_val, y_pred, pos_label=0, zero_division=0))
        metrics["brier_score"].append(brier_score_loss(y_val, y_prob))

    # Average and std across folds
    summary = {}
    for k, v in metrics.items():
        summary[f"{k}_mean"] = float(np.mean(v))
        summary[f"{k}_std"] = float(np.std(v))
    return summary


def train_and_benchmark():
    """Main training workflow."""
    logger.info("Starting Credix ML model training workflow...")
    logger.info(f"Loading raw training data from: {TRAINING_DATA_RAW}")

    if not TRAINING_DATA_RAW.exists():
        raise FileNotFoundError(f"Training dataset not found at {TRAINING_DATA_RAW}")

    raw_df = pd.read_csv(TRAINING_DATA_RAW)
    logger.info(f"Loaded raw dataset with {len(raw_df)} rows and {len(raw_df.columns)} columns.")

    # Prepare features and target (drops Gender, Married, Loan_ID)
    X, y = prepare_data(raw_df)
    logger.info(f"Prepared clean dataset with 9 audited features: {list(X.columns)}")
    logger.info(f"Target distribution: Approved(1)={sum(y==1)} ({sum(y==1)/len(y)*100:.1f}%), Rejected(0)={sum(y==0)} ({sum(y==0)/len(y)*100:.1f}%)")

    # Candidate models to benchmark
    candidates = {
        "LogisticRegression": lambda: LogisticRegression(max_iter=1000, random_state=42),
        "RandomForest": lambda: RandomForestClassifier(n_estimators=150, max_depth=6, min_samples_leaf=3, random_state=42),
        "HistGradientBoosting": lambda: HistGradientBoostingClassifier(max_iter=100, max_depth=4, min_samples_leaf=10, random_state=42),
    }

    results = {}
    logger.info("Running 5-Fold Stratified Cross-Validation on candidate models...")
    for name, factory in candidates.items():
        logger.info(f"Evaluating {name}...")
        summary = evaluate_cv(build_full_pipeline, factory, X, y, cv=5)
        results[name] = summary
        logger.info(
            f"  {name} => ROC-AUC: {summary['roc_auc_mean']:.4f} (±{summary['roc_auc_std']:.3f}), "
            f"PR-AUC: {summary['pr_auc_mean']:.4f}, "
            f"F1 (Rejected): {summary['f1_rejected_mean']:.4f}, "
            f"Brier: {summary['brier_score_mean']:.4f}"
        )

    # Champion selection: Sort by ROC-AUC and minority class F1
    champion_name = max(results.keys(), key=lambda k: results[k]["roc_auc_mean"] + results[k]["f1_rejected_mean"])
    logger.info(f"Champion model selected: {champion_name}")

    # Fit champion pipeline on the entire dataset
    logger.info(f"Fitting champion {champion_name} on the full {len(X)} training samples...")
    champion_model = candidates[champion_name]()
    final_pipeline = build_full_pipeline(champion_model)
    final_pipeline.fit(X, y)

    # Save model artifact
    MODEL_ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(final_pipeline, MODEL_ARTIFACT_PATH)
    logger.info(f"Saved fitted pipeline artifact to: {MODEL_ARTIFACT_PATH}")

    # Save metadata
    metadata = {
        "model_version": MODEL_VERSION,
        "champion_algorithm": champion_name,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "total_training_samples": len(X),
        "features": {
            "all_9_features": FEATURE_COLUMNS,
            "numerical": NUMERICAL_FEATURES,
            "categorical": CATEGORICAL_FEATURES,
        },
        "target_mapping": {"1": "Approved", "0": "Rejected"},
        "fair_lending_excluded_demographics": ["Gender", "Married"],
        "cross_validation_results": results,
        "champion_cv_metrics": results[champion_name],
    }
    save_json(metadata, METADATA_ARTIFACT_PATH)
    logger.info(f"Saved training metadata to: {METADATA_ARTIFACT_PATH}")
    logger.info("Training workflow successfully completed!")
    return final_pipeline, metadata


if __name__ == "__main__":
    train_and_benchmark()

