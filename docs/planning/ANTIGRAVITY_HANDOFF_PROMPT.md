# Antigravity Handoff — Credix (SmartLoan Predictor) Repository Memory & State

**Project Name:** Credix (SmartLoan Predictor)  
**Baseline Version:** v0.5.0 (Phases 1, 2, 3, 3.1, 4, 4.1, 4.2 & 5 Complete & Approved)  
**Next Objective:** Phase 6 — Verification, Hardening & Cloud Deployment (Render, Supabase, Vercel)  
**Last Updated:** 2026-10-30  

---

## 1. System Architecture & Topology

- **Frontend:** Next.js 14+ (App Router), TypeScript, Tailwind CSS, hosted on **Vercel**. Communicates **strictly and exclusively** with the Backend API over HTTPS. Never accesses PostgreSQL or ML directly (`D-013`).
- **Backend API:** Python 3.14 + FastAPI + SQLAlchemy 2.0 + Alembic, hosted on **Render**. Owns authentication, authorization, business rules, validation, and database persistence (`D-014`).
- **ML Subsystem:** Python scikit-learn + TreeSHAP explainability engine. Champion Random Forest model (`ROC-AUC: 0.7639`, `PR-AUC: 0.8569`, `Precision (Rejected): 92.2%`). Serialized in [`ml/inference/artifacts/model.joblib`](../../ml/inference/artifacts/model.joblib) and [`metadata.json`](../../ml/inference/artifacts/metadata.json). Collocated directly with the backend API for high-performance sub-100ms inference (`D-007`, `D-025`, `D-026`).
- **Database:** PostgreSQL on **Supabase** (with local SQLite fallback `sqlite:///./credix_dev.db` for offline dev/testing). Managed via Alembic migrations ([`backend/alembic/`](../../backend/alembic/)).

---

## 2. Core Architectural Invariants & Guardrails

1. **Fair Lending Policy (`D-023`):**
   - Prohibited demographic attributes (`Gender`, `Married`, `Race`, `Sex`) are strictly purged at the API schema boundary (`422 Unprocessable Content`).
   - They are completely omitted from training data, feature matrices, Pydantic schemas, and database snapshots to comply with the Equal Credit Opportunity Act (ECOA).
2. **Server-Derived Ownership Scoping (`D-016`, `FR-018`):**
   - User prediction history is strictly scoped by the authenticated server-side identity (`current_user.id`).
   - In cross-user probes, an unauthorized applicant querying another user's record ID receives HTTP 404, never disclosing record existence.
3. **Atomic Persistence & Rollback (`FR-014`):**
   - If ML inference or TreeSHAP execution fails or times out, the database transaction is immediately rolled back; zero uncommitted or orphaned prediction records are saved.
4. **Authoritative Request ID Tracing (`P-005`, `FR-029`):**
   - Request IDs are generated server-side via `uuid.uuid4()`. Client-supplied request IDs are ignored for internal state.
   - The same request ID is returned in `X-Request-ID` and persisted to `PredictionRecord.request_id`.
5. **Standardized Error Envelopes (`D-035`):**
   - All errors (HTTP 400, 401, 403, 404, 422, 500, 503) return a unified envelope:
     ```json
     {
       "error": {
         "code": "ERROR_CODE",
         "message": "Human-readable description.",
         "details": []
       },
       "request_id": "server-generated-uuid"
     }
     ```
6. **Security Audit Trails:**
   - Security-relevant events (`AUTH_REGISTER`, `AUTH_LOGIN_SUCCESS`, `AUTH_LOGIN_FAILURE`, `ADMIN_DASHBOARD_ACCESS`, `ADMIN_USERS_LIST_ACCESS`) are recorded in `audit_events` with strict secret/credential scrubbing.

---

## 3. Approved 9-Feature Input Schema

| Field | Type | Validation / Allowed Values | Description |
|---|---|---|---|
| `applicant_income` | Float | `> 0.0` | Primary applicant monthly income |
| `coapplicant_income` | Float | `>= 0.0` (default: 0.0) | Co-applicant monthly income |
| `loan_amount` | Float | `> 0.0` | Loan amount in thousands ($1,000s) |
| `loan_amount_term` | Int | `[12, 36, 60, 120, 180, 240, 300, 360, 480]` | Term duration in months |
| `credit_history` | Int | `0` or `1` | Credit guideline criteria flag |
| `education` | String | `"Graduate"`, `"Not Graduate"` | Education level |
| `self_employed` | String | `"Yes"`, `"No"` | Self-employment status |
| `dependents` | String | `"0"`, `"1"`, `"2"`, `"3+"` | Number of dependents |
| `property_area` | String | `"Urban"`, `"Semiurban"`, `"Rural"` | Geographic area |

---

## 4. Subsystems Status & Test Evidence

- **Frontend Subsystem (`frontend/`):** 100% verified. Next.js 14 App Router, TypeScript, Tailwind CSS, GSAP, Framer Motion, and anti-slop institutional UI. Production build passes 10/10 static routes with zero warnings.
- **ML Pipeline (`ml/`):** 100% verified. Evaluated across 5-fold CV (`ROC-AUC: 0.7639`, `Brier: 0.1513`). TreeSHAP local attribution runtime: ~0.61 ms.
- **Backend API (`backend/`):** 100% verified. 12 automated integration tests in [`backend/tests/test_backend_api.py`](../../backend/tests/test_backend_api.py) passing 100%.
- **Database (`backend/alembic/`):** Migration `001_initial_schema.py` defines `users`, `prediction_records`, and `audit_events`.
- **Audit Documentation (`docs/`):**
  - [`docs/data/DATASET_AUDIT.md`](../data/DATASET_AUDIT.md)
  - [`docs/ml/PHASE_3_COMPLETION_REPORT.md`](../ml/PHASE_3_COMPLETION_REPORT.md)
  - [`docs/ml/PHASE_3_1_FINAL_AUDIT_REPORT.md`](../ml/PHASE_3_1_FINAL_AUDIT_REPORT.md)
  - [`docs/backend/PHASE_4_1_BACKEND_AUDIT_REPORT.md`](../backend/PHASE_4_1_BACKEND_AUDIT_REPORT.md)
  - [`docs/backend/PHASE_4_2_BACKEND_HARDENING_REPORT.md`](../backend/PHASE_4_2_BACKEND_HARDENING_REPORT.md)
- **Known Deferred Items (`technical_debt.md`):**
  - `TD-001`: Service-specific environment templates (**Resolved in Phase 5**).
  - `TD-008` & `TD-014`: ML hosting topology on Render (Phase 6).
  - `TD-015`: Live Supabase PostgreSQL staging migration & connection verification (Phase 6).

---

## 5. Verification Commands for Subsequent Sessions

```bash
# 1. Run backend integration test suite (12 tests)
source .venv/bin/activate
pytest backend/tests/test_backend_api.py -v

# 2. Run local FastAPI dev server (port 8000)
uvicorn backend.app.main:app --reload --port 8000

# 3. Build & start Next.js 14 frontend (port 3000)
cd frontend
npm run build
npm run dev
```
