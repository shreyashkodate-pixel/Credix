# SmartLoan Predictor — Decision Register

**Document status:** Living register  
**Version:** 0.5.0  
**Last Updated:** 2026-10-30  
**Purpose:** Keep confirmed choices separate from proposals and unresolved questions.

## 1. Confirmed decisions

| ID | Decision | Rationale / notes |
|---|---|---|
| D-001 | Project name is SmartLoan Predictor (Credix). | Working project name. |
| D-002 | Project is intended to be portfolio-quality. | Requires documentation, tests, reproducibility, security, and a working deployed flow. |
| D-003 | Support both registered users and administrators. | Different user journeys and permission levels are required. |
| D-004 | Use PostgreSQL as the database. | Relational storage for users, prediction history, and audit records. |
| D-005 | Frontend uses Next.js + TypeScript. | Selected application frontend stack. |
| D-006 | Backend API uses Python + FastAPI. | Selected API and business-logic stack. |
| D-007 | ML service uses Python + FastAPI and scikit-learn ecosystem tools. | Separates inference from the backend API. |
| D-008 | Use three application services plus a separate database service. | Frontend, backend API, ML inference, and PostgreSQL have separate responsibilities. |
| D-009 | Frontend deployment provider is Vercel. | User-selected deployment provider. |
| D-010 | Backend API deployment provider is Render. | User-selected deployment provider. |
| D-011 | Database provider is Supabase PostgreSQL. | User-selected database provider. |
| D-012 | ML service will most likely be hosted on Render, but this is not final. | Validate resource needs, networking, startup, and costs before confirmation. |
| D-013 | Frontend must not connect directly to the database or ML service. | Keeps privileged operations and service credentials server-side. |
| D-014 | Backend owns auth, authorization, business rules, orchestration, and database persistence. | Clear security and responsibility boundary. |
| D-015 | ML service owns inference and model-specific preprocessing/explanation and does not access the database. | Keeps model-serving responsibilities isolated. |
| D-016 | Prediction history must be private to each user. | Backend-enforced record ownership (`user_id` query scoping). |
| D-017 | Show explanations with prediction results. | User explicitly prefers explanatory factors. Method depends on the eventual model. |
| D-018 | Show probability only if its meaning and validity are supported by evaluation/calibration. | Avoid misleading certainty. |
| D-019 | Google Antigravity is the primary coding IDE/AI development agent. | All implementation prompts and workflows should be tailored to Antigravity. |
| D-020 | Use phased development, tests, code review, and Git/GitHub. | Avoid broad unverified changes and preserve project history. |
| D-021 | Use the open Loan Prediction Problem benchmark dataset (Dream Housing Finance). | Audited for open educational redistribution, zero PII, and clean application-time features (resolves O-001). See `docs/data/DATASET_AUDIT.md`. |
| D-022 | Target variable is `Loan_Status` (binary: 1 = Approved, 0 = Rejected). | Represents origination underwriting outcome; observed historical ratio ~69% approved / ~31% rejected (resolves O-002). |
| D-023 | Model input schema finalized to 9 features; sensitive attributes (`Gender`, `Married`) excluded for Fair Lending. | Complies with Equal Credit Opportunity Act (ECOA) standards against demographic proxy bias; all 9 features known at application time (resolves O-003). |
| D-024 | Evaluation baseline uses 5-Fold Stratified CV with ROC-AUC, PR-AUC, minority class F1, and Brier score. | Rigorous evaluation accounting for moderate class imbalance (resolves O-004). |
| D-025 | Selected Random Forest (150 trees, max_depth 6) with median/mode imputation, standard scaling, and OneHotEncoder. | Highest mean ROC-AUC (0.7639), PR-AUC (0.8569), and 92.2% precision on Rejected class (resolves O-005). |
| D-026 | Use TreeSHAP for local feature attribution explanations. | Sub-15ms local attribution without slow background sampling (resolves O-006). |
| D-027 | Display predicted approval probability alongside TreeSHAP factors. | Validated Brier score (0.1513) demonstrates solid probability calibration (resolves O-007). |
| D-028 | Standardize artifact serialization in `ml/inference/artifacts/` (`model.joblib` and `metadata.json`). | Self-contained, version-controlled metadata ensuring traceability (resolves O-016). |
| D-029 | Standardize all versioned backend API endpoints under `/api/v1/*`. | Clear API versioning and backward compatibility boundary (resolves P-002). Root `/health` serves liveness probes. |
| D-030 | Use JWT Bearer tokens with native `bcrypt` password hashing for authentication. | Stateless, cross-origin compatible token auth between Vercel and Render with safe 72-byte password hashing (resolves O-008). |
| D-031 | Implement RBAC with `user` and `admin` roles; admin endpoints require `admin` role. | Enforces administrative boundary (`403 Forbidden` for non-admin accounts; resolves O-010). Email verification deferred post-MVP (resolves O-009). |
| D-032 | Use SQLAlchemy 2.0 ORM with Alembic migration framework for database schema management. | Explicit schema versioning and programmatic rollback capabilities across dev and prod environments (resolves P-003, O-012). |
| D-033 | Standardize UUID strings (`uuid.uuid4()`) as primary keys across all database tables. | Prevents sequential ID harvesting and collision risks across distributed systems (resolves P-004). |
| D-034 | Use hybrid relational schema: typed metadata columns + JSON/JSONB for input snapshots and TreeSHAP attributions. | Enables performant indexing on status/dates while preserving full fidelity of model explanations and raw inputs (resolves TD-007). |
| D-035 | Standardize JSON error envelopes and inject `X-Request-ID` and `X-Response-Time-Ms` headers. | Consistent client error consumption and distributed request traceability (resolves P-005, FR-029). |
| D-036 | Configure cascade deletion (`ondelete="CASCADE"`) on user foreign keys. | Guarantees clean GDPR/CCPA data cleanup when user accounts are purged (resolves O-011). |
| D-037 | Use Next.js 14+ (App Router), TypeScript, Tailwind CSS, GSAP, and Framer Motion for frontend. | Combines high-density institutional fintech design (anti-slop) with precision GSAP tickers and snappy Framer Motion transitions (resolves Phase 5 design). |
| D-038 | Enforce ECOA Fair Lending and 9-feature client validation on loan application form. | Replicates backend Pydantic bounds, excludes sensitive demographic fields, and displays compliance notices. |

## 2. Proposed decisions needing validation

| ID | Proposal | Why not final |
|---|---|---|
| P-001 | Use Docker Compose for local multi-service development. | Confirm it is useful and practical for the selected stack and local environment. |
| P-006 | Restrict ML calls through private networking or service-to-service authentication. | Dependent on whether standalone microservice or colocation is selected for Phase 6 deployment. |

## 3. Open decisions

| ID | Question | Status | Needed by |
|---|---|---|---|
| O-001 | Which dataset is suitable, licensed, and available for this task? | **Resolved by D-021** | Phase 2 |
| O-002 | What exactly does the target label represent, and how reliable is it? | **Resolved by D-022** | Phase 2 |
| O-003 | What fields are available, meaningful, and permitted as model inputs? | **Resolved by D-023** | Phase 2 |
| O-004 | Which evaluation metrics and acceptance thresholds are defensible? | **Resolved by D-024** | Phase 3 |
| O-005 | Which model and preprocessing pipeline should be selected? | **Resolved by D-025** | Phase 3 |
| O-006 | Which explanation technique is suitable for the selected model? | **Resolved by D-026** | Phase 3 |
| O-007 | Is a probability score valid and appropriately calibrated for display? | **Resolved by D-027** | Phase 3 |
| O-008 | Cookie-based sessions or JWT access/refresh tokens? | **Resolved by D-030** | Phase 4 |
| O-009 | Is email verification/password reset in the MVP? | **Resolved by D-031** (Deferred post-MVP) | Phase 4 |
| O-010 | What admin operations and permissions are needed? | **Resolved by D-031** | Phase 4 |
| O-011 | What is the account deletion, prediction retention, and audit policy? | **Resolved by D-036** | Phase 4 |
| O-012 | What database ORM and migration tool will be used? | **Resolved by D-032** | Phase 4 |
| O-013 | What is the backend-to-ML service authentication/network design? | Open | Phase 6 |
| O-014 | Is Render suitable for the ML service given model size, memory, startup, and cost? | Open | Phase 6 |
| O-015 | What performance, availability, and rate-limit targets should be set? | Open | Phase 6 |
| O-016 | What is the model artifact storage, release, rollback, and retraining process? | **Resolved by D-028** | Phase 3 |

## 4. Decision change policy

- Do not silently replace a confirmed decision.
- If new evidence requires a change, document the proposed change, rationale, impact, and affected documents.
- Keep dataset-dependent decisions provisional until the audit is complete.
- Update the PRD, SRS, architecture, API contract, database design, and this register when a decision changes.
- Antigravity must report assumptions and unresolved decisions instead of inventing values or silently expanding scope.
