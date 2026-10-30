# Credix — Machine Learning Subsystem (`ml/`)

This directory contains the complete offline training pipeline, benchmark evaluations, and production inference service for **Credix (SmartLoan Predictor)**.

---

## 1. Directory Architecture

```text
ml/
├── training/                      # OFFLINE (experiments + model building)
│   ├── data/
│   │   ├── raw/                  # train.csv (614 rows benchmark data)
│   │   ├── processed/            # Cached splits (optional)
│   │   └── external/             # External/benchmark data
│   │
│   ├── scripts/
│   │   ├── train.py              # Main training & cross-validation entrypoint
│   │   ├── evaluate.py           # Metrics & calibration curve assessment
│   │   └── generate_data.py      # Optional synthetic data generator
│   │
│   ├── experiments/              # Logs & experiment notes
│   └── requirements.txt          # Training dependencies (pandas, sklearn, shap, matplotlib)
│
├── inference/                    # PRODUCTION (used by backend / Render)
│   ├── model/
│   │   ├── loader.py             # Thread-safe artifact loader with caching
│   │   └── predictor.py          # Core predict() & local TreeSHAP factor generator
│   │
│   ├── preprocessing/
│   │   └── preprocess.py         # 9-feature input validator (rejects prohibited demographics)
│   │
│   ├── services/
│   │   └── prediction_service.py # Main orchestration entrypoint for inference
│   │
│   ├── artifacts/                # Serialized model & metadata
│   │   ├── model.joblib          # Fitted scikit-learn Pipeline
│   │   └── metadata.json         # Versioning, metrics, and feature lists
│   │
│   ├── config/
│   │   └── settings.py           # Environment configuration & ports
│   │
│   └── api/                      # Standalone FastAPI service
│       ├── routes.py             # POST /predict, GET /ready, GET /health
│       └── schema.py             # Pydantic request/response models
│
├── pipeline/                     # CORE LOGIC (shared orchestration)
│   ├── __init__.py
│   └── pipeline.py               # Shared ColumnTransformer & preprocessing logic
│
├── common/                       # SHARED UTILITIES
│   ├── __init__.py
│   ├── constants.py              # Audited 9 features, Fair Lending exclusions, labels
│   └── utils.py                  # Logging, JSON encoding with NumPy support
│
└── README.md                     # This document
```

---

## 2. Fair Lending Policy ([`D-023`](../docs/planning/DECISION_REGISTER.md))

In strict compliance with the Equal Credit Opportunity Act (ECOA) and ethical AI standards, **`Gender`** and **`Married`** are permanently excluded from:
- Raw data ingestion (`prepare_data()`)
- Preprocessing transformations (`ColumnTransformer`)
- Inference validation (`validate_and_format_input()`)

Any inference request containing demographic attributes is immediately rejected with HTTP `422 Unprocessable Entity`.

---

## 3. Benchmarked Model Results

Candidate models were evaluated using **5-Fold Stratified Cross-Validation**:

| Algorithm | Mean ROC-AUC | Mean PR-AUC | Mean Accuracy | Precision (Rejected) | Brier Score (Loss) | Status |
|---|---|---|---|---|---|---|
| **LogisticRegression** | 0.7492 | 0.8346 | 80.8% | 90.2% | 0.1539 | Baseline |
| **RandomForest** | **0.7639** | **0.8569** | **81.1%** | **92.2%** | **0.1513** | **Champion Selected** |
| **HistGradientBoosting** | 0.7386 | 0.8367 | 77.0% | 73.0% | 0.1731 | Evaluated |

### Why Random Forest Won:
1. **Highest Discriminative Ability:** Highest ROC-AUC (0.7639) and PR-AUC (0.8569).
2. **Superior Precision on Minority Class:** When predicting `Rejected` (class `0`), Random Forest achieves **92.2% precision** (with 43.3% recall), minimizing false rejections while maintaining a defensible portfolio trade-off.
3. **Comparative Probability Calibration:** Lowest Brier Score (0.1513) among candidate models. *(Note: Brier score is a comparative ranking metric among tested models, not proof of real-world calibration across dynamic economic cycles).*
4. **Fast, Native TreeSHAP:** Isolated TreeSHAP computes feature attributions locally in under 1 ms (~0.61 ms), enabling an end-to-end inference and explanation latency of ~43 ms without slow Monte-Carlo background sampling.

---

## 4. Local Execution & Quickstart

### Setup Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r ml/training/requirements.txt
```

### Train Champion Model
```bash
python ml/training/scripts/train.py
```
*Outputs: `ml/inference/artifacts/model.joblib` and `ml/inference/artifacts/metadata.json`.*

### Run Evaluation Diagnostics
```bash
python ml/training/scripts/evaluate.py
```

### Run Python Inference in Code
```python
from ml.inference.services.prediction_service import PredictionService

service = PredictionService()

applicant = {
    "applicant_income": 6500.0,
    "coapplicant_income": 2000.0,
    "loan_amount": 130.0,
    "loan_amount_term": 360,
    "credit_history": 1,
    "education": "Graduate",
    "self_employed": "No",
    "dependents": "0",
    "property_area": "Semiurban",
}

result = service.predict(applicant)
print(result)
# Output:
# {
#   "outcome": "Approved",
#   "probability": 0.8527,
#   "model_version": "1.0.0",
#   "algorithm": "RandomForest",
#   "explanation": {
#     "method": "TreeSHAP",
#     "factors": [...]
#   }
# }
```

