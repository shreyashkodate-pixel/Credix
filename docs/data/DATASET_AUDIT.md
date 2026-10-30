# Credix — Dataset Audit & Feature Specification

**Document Type:** Data Card & Audit Specification  
**Phase:** Phase 2 Deliverable  
**Baseline Version:** 0.2.0  
**Status:** Approved Baseline  
**Last Updated:** 2026-10-30  
**Related Documents:** [`docs/planning/PRD.md`](../planning/PRD.md), [`docs/planning/SRS.md`](../planning/SRS.md), [`docs/planning/API_CONTRACT.md`](../planning/API_CONTRACT.md), [`docs/planning/DECISION_REGISTER.md`](../planning/DECISION_REGISTER.md)

---

## 1. Executive Summary & Purpose

Credix is an AI/ML-assisted loan outcome prediction web application designed to demonstrate an end-to-end, portfolio-quality software architecture. 

During Phase 2, candidate datasets were vetted to establish a reliable, legally compliant, and defensible foundation for model training (Phase 3), backend API contracts (Phase 4), and user interface workflows (Phase 5). This document records the dataset provenance, licensing terms, target label semantics, data leakage audit, Fair Lending demographic exclusions, and the finalized 9-feature model input dictionary.

---

## 2. Dataset Provenance & Licensing

- **Dataset Identity:** Loan Prediction Problem Dataset (originating from the canonical Dream Housing Finance benchmark).
- **Source Platform:** Open benchmark widely distributed via Kaggle and machine learning education repositories.
- **Licensing & Usage Rights:**
  - Available under open educational and permissive terms for research, portfolio demonstration, and benchmark reproducibility.
  - Contains no proprietary corporate IP, commercial trade secrets, or active live lending records.
- **PII & Privacy Audit:**
  - The dataset contains zero Personally Identifiable Information (no real applicant names, Social Security Numbers, phone numbers, email addresses, or physical street addresses).
  - Individual rows are keyed by synthetic identifiers (`Loan_ID`), which are discarded during feature preprocessing.

---

## 3. Target Label Semantics & Distribution

The target variable for Credix represents an application-time origination decision.

### 3.1 Formal Definition

| Attribute | Specification |
|---|---|
| **Raw Column Name** | `Loan_Status` |
| **Data Type** | Binary String (`Y`, `N`) mapped to Integer (`1`, `0`) |
| **Class `1` (Positive)** | `Approved` (`Y`) — The loan application satisfies credit criteria. |
| **Class `0` (Negative)** | `Rejected` (`N`) — The loan application does not satisfy credit criteria. |
| **Lifecycle Point** | **Origination Time** (prior to disbursement or repayment). |

### 3.2 Observed Distribution & Class Balance

- **Total Historical Records:** ~614 applicant entries.
- **Approved (`Y` / `1`):** ~422 instances (~68.7%).
- **Rejected (`N` / `0`):** ~192 instances (~31.3%).
- **Imbalance Assessment:** Moderate class imbalance (~2.2 : 1). 
- **Phase 3 Modeling Guidance:** While not severely skewed, accuracy alone is insufficient. Phase 3 training must monitor Precision, Recall, F1-Score, and PR-AUC / ROC-AUC, especially for the minority class (`Rejected`).

---

## 4. Data Leakage & Temporal Boundary Audit

A critical failure mode in credit risk modeling is **target leakage** (training a model on features that are only generated *after* the loan is granted).

### 4.1 Leakage Evaluation Findings

- **Temporal Check:** All candidate features represent information provided by the applicant on their initial application form or retrieved from credit bureaus at the exact time of application.
- **No Post-Origination Columns:** Unlike secondary-market performance datasets (e.g., LendingClub), this dataset contains no payment transaction logs, delinquent payment dates, collection fees, or payoff timestamps.
- **Conclusion:** The data leakage risk ([`TD-010`](../../technical_debt.md)) is **zero** for the selected dataset.

---

## 5. Responsible AI & Fair Lending Policy

In consumer credit evaluation, legal and ethical standards (such as the US *Equal Credit Opportunity Act* - ECOA and Regulation B) prohibit lenders from making credit determinations on the basis of protected characteristics.

### 5.1 Omission of Sensitive Demographic Attributes

The raw benchmark dataset contains two demographic features that Credix **explicitly excludes** from the feature pipeline:

1. **`Gender` (Male / Female):**
   - **Reason for Exclusion:** Protected class under fair lending regulations. Using gender as a model input risks encoding historical lending disparities and proxy discrimination.
2. **`Married` (Yes / No):**
   - **Reason for Exclusion:** Marital status is a protected attribute in consumer credit evaluation. Creditworthiness should be established purely through applicant income, obligations, credit history, and collateral adequacy.

> [!IMPORTANT]
> **Fair Lending Compliance:**  
> Neither `Gender` nor `Married` will be collected in the frontend UI, accepted by the Backend API, stored in prediction records, or supplied to the ML inference pipeline. This policy is permanently codified in [`D-023`](../planning/DECISION_REGISTER.md).

---

## 6. Finalized 9-Feature Input Schema

The finalized input schema consists of **9 high-signal, accessible features** categorized into applicant financials, loan parameters, credit history, and application context.

| # | Feature Key | Type | UI Form Control | Units / Allowed Values | Validation Range | Nullable | Example |
|---|---|---|---|---|---|---|---|
| 1 | `applicant_income` | Float | Currency Input ($) | Monthly currency | $> 0.0$ | No | `5000.0` |
| 2 | `coapplicant_income` | Float | Currency Input ($) | Monthly currency | $\ge 0.0$ (0 if none) | No | `1500.0` |
| 3 | `loan_amount` | Float | Currency Input ($k) | Thousands ($1,000s) | $> 0.0$ | No | `120.0` |
| 4 | `loan_amount_term` | Int | Dropdown / Slider | Months | $\in \{12, 36, 60, 120, 180, 240, 300, 360, 480\}$ | No | `360` |
| 5 | `credit_history` | Int | Radio / Toggle | Binary indicator | $\in \{0, 1\}$ (`1` = Meets guidelines, `0` = Does not) | No | `1` |
| 6 | `education` | String | Radio Group | Enum | $\in \{\text{"Graduate"}, \text{"Not Graduate"}\}$ | No | `"Graduate"` |
| 7 | `self_employed` | String | Radio Group | Enum | $\in \{\text{"Yes"}, \text{"No"}\}$ | No | `"No"` |
| 8 | `dependents` | String | Dropdown / Pills | Enum / Ordinal | $\in \{\text{"0"}, \text{"1"}, \text{"2"}, \text{"3+"}\}$ | No | `"0"` |
| 9 | `property_area` | String | Segmented Control | Enum | $\in \{\text{"Urban"}, \text{"Semiurban"}, \text{"Rural"}\}$ | No | `"Semiurban"` |

### 6.1 Field Definitions & UI Validation Rules

1. **`applicant_income`**: Gross monthly income of the primary applicant. Must be strictly positive.
2. **`coapplicant_income`**: Gross monthly income of an additional co-applicant or guarantor. Can be `0.0` if single applicant.
3. **`loan_amount`**: Principal loan amount requested, expressed in thousands of dollars (e.g., `$120,000` is submitted as `120.0`).
4. **`loan_amount_term`**: Duration of the loan in months. Standard terms: 360 (30-year), 180 (15-year), 240 (20-year), 120 (10-year).
5. **`credit_history`**: Direct proxy for credit bureau status: `1` indicates acceptable past credit record; `0` indicates delinquent history or severe derogatory marks.
6. **`education`**: Highest educational attainment completed by the primary applicant.
7. **`self_employed`**: Whether the primary applicant is self-employed or owns a business.
8. **`dependents`**: Number of dependent family members supported by the applicant's income.
9. **`property_area`**: Geographic categorization of the underlying property collateral.

---

## 7. Downstream System Mapping

- **Backend API:** The Pydantic model `PredictionCreateRequest` in `POST /predictions` will validate these exact 9 keys with typed field bounds.
- **Database Schema:** `prediction_records.inputs` will store a JSON snapshot containing these 9 keys with schema versioning.
- **Frontend UI:** The application form will render 9 clean input widgets, structured into:
  - *Applicant Financials:* Income, Co-applicant Income, Employment, Education.
  - *Loan Details:* Amount, Term, Property Location.
  - *Credit Profile:* Credit History, Dependents.
- **Inference Pipeline:** The ML service pipeline will receive these 9 features, perform one-hot/ordinal encoding, apply trained scaling transformations, and yield the binary prediction and TreeSHAP attribution factors.

