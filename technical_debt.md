# Credix — Technical Debt & Architectural Deferred Items

**Document Status:** Living Register  
**Baseline Version:** 0.2.0  
**Last Updated:** 2026-10-30  
**Related Documents:** [`docs/planning/DECISION_REGISTER.md`](docs/planning/DECISION_REGISTER.md), [`docs/data/DATASET_AUDIT.md`](docs/data/DATASET_AUDIT.md), [`docs/planning/SYSTEM_ARCHITECTURE.md`](docs/planning/SYSTEM_ARCHITECTURE.md)

---

## 1. Overview & Strategy

Technical debt in Credix is divided into two categories:
1. **Intentional Deferred Decisions**: Architectural or implementation choices intentionally postponed to preserve phased discipline (e.g., waiting for the dataset audit before defining column types).
2. **Provisional Scaffolding Debt**: Temporary placeholders or simplified contracts that must be hardened before public deployment (e.g., provisional environment templates, tentative hosting providers).

This register documents every known area of technical debt, its current status, associated risks, and the targeted resolution phase.

---

## 2. Technical Debt Register

| ID | Category | Item | Current Status | Risk / Impact | Target Phase |
|---|---|---|---|---|---|
| **TD-001** | Configuration | Service-specific `.env.example` templates missing | Deferred intentionally | Developers might guess service variable names if created without service directories. | Phase 4 & 5 |
| **TD-002** | API Design | API versioning prefix (`/api/v1` vs unversioned) | Proposal P-002 (Unconfirmed) | Breaking route changes if frontend and backend diverge on prefix conventions. | Phase 4 |
| **TD-003** | Security / Auth | Auth strategy: HttpOnly Cookie vs JWT Tokens | Open Decision O-008 | Cross-origin issues between Vercel (frontend) and Render (backend) if cookie `SameSite`/`Secure` flags or CORS are misconfigured. | Phase 4 |
| **TD-004** | Security / Auth | Admin user provisioning & RBAC granularity | Open Decisions O-009, O-010 | Manual database edits needed to grant admin role unless an initial seed/CLI command is built. | Phase 4 |
| **TD-005** | Database | Database ORM & migration framework unselected | Proposal P-003 / O-012 | Schema drift if migrations are not standardized early in backend implementation. | Phase 4 |
| **TD-006** | Database | Primary key strategy (UUID vs BigInt) | Proposal P-004 | Migrations required later if ID format changes after initial tables are created. | Phase 4 |
| **TD-007** | Database | Typed columns vs JSONB for inputs & explanations | Open Decision O-011 | Querying and indexing flexibility vs schema rigidity for model input snapshots. | Phase 4 |
| **TD-008** | Infrastructure | ML Service hosting on Render (Free/Starter tier) | Tentative (D-012, O-014) | Cold starts (30-60s) and memory exhaustion (512MB limit) could fail inference under load. | Phase 3 / 6 |
| **TD-009** | Infrastructure | Backend-to-ML Service private networking vs Token Auth | Open Decision O-013 / P-006 | ML inference service could be accidentally exposed to the public internet if not protected. | Phase 4 / 6 |
| **TD-010** | ML Pipeline | Target label ambiguity & data leakage risk | **Resolved in Phase 2** (D-021, D-022, D-023) | Model predicting outcome using post-application features (target leakage) or proxy bias. | Phase 2 |
| **TD-011** | ML Pipeline | Model explainability technique unbenchmarked | Open Decision O-006 | SHAP computation may introduce significant inference latency if computed synchronously in HTTP request. | Phase 3 |
| **TD-012** | ML Pipeline | Probability calibration policy undefined | Open Decision O-007 | Raw classifier outputs may be misconstrued as true probabilities by end users. | Phase 3 |
| **TD-013** | Operations | Error envelope & Request ID correlation format | Proposal P-005 | Inconsistent API error handling in frontend if backend responses lack unified envelope. | Phase 4 |
| **TD-014** | Governance | Data retention, account deletion, and audit policy | Open Decision O-011 | Unclear cascade deletion rules for user accounts and historical predictions. | Phase 4 |

---

## 3. Detailed Debt Descriptions & Mitigation Plans

### TD-001: Service-Specific Environment Templates
- **Description:** Only a shared root `.env.example` exists. Service templates (`backend/.env.example`, `frontend/.env.example`, `ml/.env.example`) have been deliberately deferred until application service directories are created.
- **Mitigation:** When `backend/`, `frontend/`, and `ml/` directories are initialized during Phases 3, 4, and 5, create dedicated `.env.example` files containing only the exact configuration needed for that service. Never expose backend secrets in `NEXT_PUBLIC_*` variables.

### TD-003: Authentication Across Independent Hosting Origins
- **Description:** Frontend is hosted on Vercel (`credix.vercel.app` or custom domain) and Backend API on Render (`credix-api.onrender.com`).
- **Risk:** If HttpOnly cookies are used across different domains, modern browsers may block third-party cookies unless strict `SameSite=None; Secure` headers and domain delegation are configured. Conversely, storing JWT tokens in browser storage introduces XSS risks.
- **Mitigation:** Evaluate cookie-based authentication with Next.js API route proxying (BFF pattern) or secure short-lived JWT access tokens paired with HttpOnly refresh cookies before implementing Phase 4 auth.

### TD-008: Render Cold Starts & Memory Constraints for ML Service
- **Description:** Render starter/free web services idle down after inactivity and provide limited RAM (512MB). Python processes with scikit-learn, numpy, and dependencies may approach this threshold.
- **Risk:** High latency on first request after idle (30–60s) or process kill (OOM).
- **Mitigation:** Benchmark the trained model package size and memory footprint during Phase 3. If Render starter constraints are exceeded, evaluate:
  1. Bundling inference into the Backend API service (if model is lightweight), or
  2. Upgrading the Render instance tier, or
  3. Deploying the ML service to a serverless container platform with faster cold starts (e.g., Google Cloud Run).

### TD-010: Target Label Ambiguity & Data Leakage Risk (RESOLVED — Phase 2)
- **Status:** Resolved in Phase 2 via [`docs/data/DATASET_AUDIT.md`](docs/data/DATASET_AUDIT.md) and [`D-021`](docs/planning/DECISION_REGISTER.md), [`D-022`](docs/planning/DECISION_REGISTER.md), [`D-023`](docs/planning/DECISION_REGISTER.md).
- **Resolution Summary:**
  1. Selected the canonical Loan Prediction Problem benchmark dataset.
  2. Fixed target variable to binary `Loan_Status` (`1` = Approved, `0` = Rejected), representing application-time origination outcomes (~69% approved / ~31% rejected).
  3. Conducted temporal leakage audit: confirmed zero post-origination features exist in the candidate feature pool.
  4. Enforced Fair Lending policy: permanently excluded protected demographic attributes (`Gender`, `Married`) to prevent historical proxy bias, establishing a clean 9-feature schema.

### TD-011: Synchronous Model Explainability Latency
- **Description:** Generating KernelSHAP or feature attribution explanations per prediction can take hundreds of milliseconds to multiple seconds on CPU.
- **Risk:** Backend API prediction requests (`POST /predictions`) timing out or degrading UX.
- **Mitigation:** In Phase 3, prioritize TreeSHAP (for tree-based models like Random Forest/XGBoost) or pre-calculated linear coefficients over slow model-agnostic explanation methods.

---

## 4. Maintenance Guidelines

1. **Review Frequency:** Update this document at the start and end of every development phase.
2. **Resolution Tracking:** When a technical debt item is resolved, record the resolving commit, mark status as `Resolved`, and update associated documentation.
3. **No Hidden Debt:** If a temporary workaround or stub is introduced in code, immediately log a new `TD-xxx` entry in this register.

