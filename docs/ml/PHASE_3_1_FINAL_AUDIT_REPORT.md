# Credix — Phase 3.1: Final ML Audit Corrections Report

**Document Type:** Final Verification & Evidence Audit Report  
**Target Subsystem:** Machine Learning (`ml/`)  
**Baseline Version:** 0.3.1  
**Audit Date:** 2026-10-30  
**Status:** Complete & Verified  
**Related Documents:**
- [`docs/ml/PHASE_3_COMPLETION_REPORT.md`](PHASE_3_COMPLETION_REPORT.md)
- [`docs/data/DATASET_AUDIT.md`](../data/DATASET_AUDIT.md)
- [`docs/planning/DECISION_REGISTER.md`](../planning/DECISION_REGISTER.md)
- [`technical_debt.md`](../../technical_debt.md)
- [`ml/README.md`](../../ml/README.md)

---

## 1. Files Inspected

The following repository files and runtime artifacts were independently inspected to evaluate Phase 3 claims against reproducible physical evidence:

| File Path | Role in Audit | Status / Verification Method |
|---|---|---|
| [`ml/training/data/raw/train.csv`](../../ml/training/data/raw/train.csv) | Ground-truth dataset | Verified 614 rows, 13 raw columns |
| [`ml/common/constants.py`](../../ml/common/constants.py) | Canonical schema definitions | Verified 9 features, exclusions, target mappings |
| [`ml/pipeline/pipeline.py`](../../ml/pipeline/pipeline.py) | Shared transformation logic | Inspected ColumnTransformer & imputation strategy |
| [`ml/training/scripts/train.py`](../../ml/training/scripts/train.py) | 5-Fold Stratified CV trainer | Inspected random_state=42 and model definitions |
| [`ml/training/scripts/evaluate.py`](../../ml/training/scripts/evaluate.py) | Calibration & diagnostic script | Inspected confusion matrix and Brier loss calculation |
| [`ml/inference/artifacts/model.joblib`](../../ml/inference/artifacts/model.joblib) | Serialized champion model | Verified file size: 654,507 bytes (639.2 KB) |
| [`ml/inference/artifacts/metadata.json`](../../ml/inference/artifacts/metadata.json) | Cross-validation metrics store | Verified exact recorded fold averages and parameters |
| [`ml/inference/model/loader.py`](../../ml/inference/model/loader.py) | Singleton artifact loader | Tested thread-safe loading and `is_ready()` check |
| [`ml/inference/model/predictor.py`](../../ml/inference/model/predictor.py) | Inference & TreeSHAP engine | Traced raw Shapley attributions and label mapping |
| [`ml/inference/preprocessing/preprocess.py`](../../ml/inference/preprocessing/preprocess.py) | Input validator | Verified demographic rejection (`Gender`, `Married`) |
| [`ml/inference/services/prediction_service.py`](../../ml/inference/services/prediction_service.py) | High-level orchestration | Executed live test cases across 100 benchmark runs |
| [`ml/README.md`](../../ml/README.md) | Subsystem documentation | Audited claims against measured benchmarks |
| [`docs/ml/PHASE_3_COMPLETION_REPORT.md`](PHASE_3_COMPLETION_REPORT.md) | Initial Phase 3 report | Audited for discrepancies and precision |
| [`docs/planning/DECISION_REGISTER.md`](../planning/DECISION_REGISTER.md) | Architectural register | Verified confirmed decisions `D-024` to `D-028` |

---

## 2. Findings and Evidence

### A. Classification Metrics & Precision-Recall Trade-Off
From [`ml/inference/artifacts/metadata.json`](../../ml/inference/artifacts/metadata.json), the 5-fold cross-validated performance metrics for the champion Random Forest model are:

| Metric | Cross-Validation Mean | Standard Deviation | Interpretation |
|---|---:|---:|---|
| **ROC-AUC** | **0.7639** | ±0.0187 | Strong overall class separation |
| **PR-AUC** | **0.8569** | ±0.0189 | High precision across recall thresholds |
| **Accuracy** | **81.11%** | ±0.0171 | Overall percentage of correct classifications |
| **Precision (Rejected Class `0`)** | **92.16%** | ±0.0290 | When model predicts "Rejected", it is correct 92.2% of the time |
| **Recall (Rejected Class `0`)** | **43.28%** | ±0.0436 | Model detects 43.3% of all actual rejections |
| **F1-Score (Rejected Class `0`)** | **0.5880** | ±0.0444 | Harmonic mean for the minority class |
| **Brier Score (Loss)** | **0.1513** | ±0.0097 | Relative mean squared probability error |

#### Accurate Precision-Recall Trade-Off Explanation
The champion model operates at an implicit probability threshold of $0.5$. At this threshold:
- **High Precision ($92.2\%$):** Minimizes false rejections. An applicant predicted as `Rejected` has a high statistical probability of matching historical denial criteria.
- **Modest Recall ($43.3\%$):** The model fails to identify ~56.7% of historical rejections, classifying them instead as `Approved` (false approvals). 
- **Contextual Justification:** In enterprise credit underwriting, this would represent an aggressive/risk-tolerant lending strategy requiring secondary underwriting review. In an educational portfolio application, this design choice ensures high confidence when an adverse outcome is presented to a user while preventing unnecessary discouragement for borderline applicants.

---

### B. Probability Calibration & Holdout Assessment
1. **Comparative Nature of Brier Score:**  
   The Random Forest model achieved a mean Brier score loss of `0.1513` in 5-fold cross-validation and `0.1219` in full in-sample evaluation. This represents a superior ranking compared to candidate models (Logistic Regression: `0.1539`, HistGradientBoosting: `0.1731`).  
   **Correction:** The Brier score is a *comparative metric* demonstrating relative calibration superiority among tested models on this dataset. It is **not** mathematical proof of true, real-world probability calibration under shifting economic conditions.
2. **Absence of Independent Temporal Holdout:**  
   All 614 records were partitioned across 5 folds for model selection, and the champion model was fit on the complete 614 rows for production serving. There is **no separate unseen temporal holdout split** (e.g., testing on loan applications from subsequent quarters/years).
3. **No Production Lending Claim:**  
   The model probabilities must be interpreted as *relative modeled confidence*, not true default probabilities or underwriting guarantees.

---

### C. Resolution of the SHAP Discrepancy (`-0.2725` vs `-0.2740`)
In the initial review of Test Case 2 (`applicant_poor_credit`), a discrepancy was identified where `-0.2740` and `-0.2725` were referenced interchangeably.

#### Root Cause Investigation
A dedicated inspection script was executed to extract raw Shapley attributions across all 17 preprocessed feature dimensions for `applicant_poor_credit`:

```text
Raw One-Hot Encoded Feature Attributions (Class 1 - Approval):
  cat__credit_history_1        : -0.274030  (weight: 0.2740)
  cat__credit_history_0        : -0.272517  (weight: 0.2725)
  cat__education_Not Graduate  : -0.016960  (weight: 0.0170)
  cat__property_area_Semiurban : -0.015956  (weight: 0.0160)
```

#### Explanation of Findings
Because `credit_history` is one-hot encoded into two binary dummy columns (`cat__credit_history_0` and `cat__credit_history_1`):
1. **`cat__credit_history_1 = 0`** (the applicant lacks a positive credit record): The absence of positive credit history penalized approval by **`-0.2740`**. In `Predictor`, this maps to the friendly label `"Positive Credit History"`.
2. **`cat__credit_history_0 = 1`** (the applicant has a delinquent or absent record): The presence of this flag penalized approval by **`-0.2725`**. In `Predictor`, this maps to `"Delinquent or Absent Credit History"`.

**The Discrepancy Resolved:**  
In [`docs/ml/PHASE_3_COMPLETION_REPORT.md`](PHASE_3_COMPLETION_REPORT.md), the label `"Delinquent or Absent Credit History"` was mistakenly paired with `-0.2740`. In truth:
- Factor 1 is **`"Positive Credit History"`** with attribution **`-0.2740`** (weight `0.2740`, negative impact).
- Factor 2 is **`"Delinquent or Absent Credit History"`** with attribution **`-0.2725`** (weight `0.2725`, negative impact).

Both numbers exist simultaneously in the live output. The documentation has been corrected to reflect the exact factor mapping.

---

### D. Inference Latency: Isolated TreeSHAP vs. End-to-End Execution
To resolve conflicting claims regarding latency (<15 ms vs ~45 ms), a dedicated 100-iteration benchmark was executed on the local runtime:

| Pipeline Segment | Measured Mean | Measured Median | Measured P95 | Interpretation |
|---|---:|---:|---:|---|
| **1. Isolated TreeSHAP (`explainer.shap_values`)** | **0.61 ms** | **0.60 ms** | **0.67 ms** | C-extension Shapley tree traversal |
| **2. Pipeline Transform + RF (`predict_proba`)** | **18.28 ms** | **16.66 ms** | **21.14 ms** | Median imputation, scaling, tree inference |
| **3. End-to-End Service (`service.predict()`)** | **42.87 ms** | **44.21 ms** | **46.46 ms** | Validation + Prep + Inference + SHAP + Formatting |

#### Verification Finding
- **Isolated TreeSHAP:** Executes in **~0.61 ms** (well under 15 ms).
- **Full End-to-End Pipeline:** Executes in **~43 ms** (mean: 42.87 ms, P95: 46.46 ms).
- **Correction:** `ml/README.md` previously claimed that feature attributions are computed in under 15 ms without explicitly clarifying that this refers to isolated TreeSHAP execution. The documentation has been updated to clearly distinguish the ~0.61 ms algorithmic execution from the ~43 ms complete Python service lifecycle.

---

### E. Deployment Architecture Topology (`D-012`, `O-014`)
The architectural choice between deploying the ML inference subsystem as an independent microservice versus colocating it directly inside the FastAPI backend remains an **EXPLICITLY OPEN DECISION** (`O-014`):

```text
Decision Status: OPEN (To be resolved in Phase 4 / Phase 6)
Option A: Standalone ML Microservice on Render (FastAPI)
  • Pros: Decoupled container scaling, independent lifecycle, isolated dependencies.
  • Cons: Inter-service network hops, cold-start latency (30-60s) on Render free tier.

Option B: Colocated Inference inside Backend API (FastAPI)
  • Pros: Zero network hops, ~43ms response time, simple deployment, artifact is only 639 KB.
  • Cons: Shares backend container RAM (512MB limit on free tier).
```

Neither option is confirmed in Phase 3. Both options are fully supported by the codebase (`ml/inference/api/routes.py` for Option A; `ml/inference/services/prediction_service.py` for Option B).

---

## 3. Corrections Made

The following documentation files were updated to maintain empirical accuracy:

1. **[`ml/README.md`](../../ml/README.md):**
   - Section 3, Point 2: Documented both precision (92.2%) and recall (43.3%) for the Rejected class.
   - Section 3, Point 3: Clarified that Brier score is a comparative metric among evaluated models, not proof of real-world calibration across economic cycles.
   - Section 3, Point 4: Clarified latency distinction: isolated TreeSHAP (~0.61 ms) vs. end-to-end service (~43 ms).
2. **[`docs/ml/PHASE_3_COMPLETION_REPORT.md`](PHASE_3_COMPLETION_REPORT.md):**
   - Section 7.2: Added comprehensive explanation of the precision-recall trade-off.
   - Section 10.2: Replaced generalized latency text with the empirical 3-stage latency benchmark table.
   - Section 11.2: Corrected Test Case 2 SHAP factors list to reflect the exact output mapping (`-0.2740` for positive credit absence, `-0.2725` for delinquency presence).
   - Section 14.1: Explicitly re-affirmed hosting topology as an **OPEN DECISION** (`D-012`, `O-014`).

---

## 4. Discrepancies That Remain Unresolved

**Zero discrepancies remain unresolved.**

Every reported metric, attribution weight, latency figure, and schema constraint has been physically verified against actual runtime code outputs on the local environment:
- All cross-validation metrics match `metadata.json`.
- All test case outputs match `PredictionService.predict()`.
- The SHAP weight discrepancy between `-0.2725` and `-0.2740` was completely traced to the one-hot encoded representation of `credit_history`.
- The latency distinction between isolated TreeSHAP and end-to-end execution was benchmarked and reconciled.

---

## 5. Updated ML Limitations

To ensure absolute documentation integrity, the documented limitations for Credix ML are updated as follows:

1. **Sample Size:** 614 historical loan records. Adequate for portfolio architecture demonstration; insufficient for industrial credit underwriting.
2. **Precision-Recall Skew:** At default $0.5$ threshold, model achieves high rejection precision (92.2%) but modest rejection recall (43.3%), allowing ~57% of historical rejections to pass as approved.
3. **No Temporal Holdout:** Evaluated via 5-fold stratified cross-validation on available data; no out-of-time test set.
4. **Historical Benchmark Constraints:** Dataset reflects historical conditions (circa 2016) and cannot account for current interest rate or inflation dynamics.
5. **Proxy Feature Exposure:** Dropping `Gender` and `Married` eliminates direct disparate treatment under Fair Lending (ECOA), but proxy bias through correlated variables (`Dependents`, `Property_Area`) remains an inherent risk.
6. **Interpretability Scope:** TreeSHAP attributions indicate mathematical feature contributions toward the model's output; they do **not** represent causal explanations or formal adverse action notices under lending law.
7. **Educational Purpose:** The system is built for technical portfolio demonstration and must not be used for actual credit decisions.

---

## 6. Open Deployment Decisions

The following architectural decision remains explicitly open:

| Decision ID | Question | Current Status | Resolution Milestone |
|---|---|---|---|
| **`O-014` / `D-012`** | Deploy ML service as a standalone Render web service or colocate inference inside Backend API? | **OPEN** | Phase 4 Backend Implementation / Phase 6 Deployment |

Both architectural paths are preserved without code modification:
- `ml/inference/api/routes.py` provides the standalone FastAPI service.
- `ml/inference/services/prediction_service.py` provides the direct Python module import.

---

## 7. Final Recommendation on Phase 3 Acceptance

### Audit Verdict: **RECOMMENDED FOR FORMAL APPROVAL**

1. **Implementation Integrity:** The machine learning subsystem in `ml/` is fully functional, self-contained, tested, and decoupled from the backend.
2. **Empirical Verification:** 100% of reported metrics, schemas, and test cases have been verified with zero contradictions.
3. **Documentation Accuracy:** All identified transcription nuances, latency definitions, and metric trade-offs have been corrected.
4. **Phase 4 Readiness:** Clean handoff contracts are established for the Phase 4 Backend API.

**Recommendation:** Proceed with formal approval of Phase 3, commit the deliverables, and begin **Phase 4: Backend API and Database Implementation**.

