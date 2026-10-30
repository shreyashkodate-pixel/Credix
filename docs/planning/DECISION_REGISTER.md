# SmartLoan Predictor — Decision Register

**Document status:** Living register  
**Version:** 0.2.0  
**Purpose:** Keep confirmed choices separate from proposals and unresolved questions.

## 1. Confirmed decisions

| ID | Decision | Rationale / notes |
|---|---|---|
| D-001 | Project name is SmartLoan Predictor. | Working project name. |
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
| D-016 | Prediction history must be private to each user. | Backend-enforced record ownership. |
| D-017 | Show explanations with prediction results. | User explicitly prefers explanatory factors. Method depends on the eventual model. |
| D-018 | Show probability only if its meaning and validity are supported by evaluation/calibration. | Avoid misleading certainty. |
| D-019 | Google Antigravity is the primary coding IDE/AI development agent. | All implementation prompts and workflows should be tailored to Antigravity. |
| D-020 | Use phased development, tests, code review, and Git/GitHub. | Avoid broad unverified changes and preserve project history. |
| D-021 | Use the open Loan Prediction Problem benchmark dataset (Dream Housing Finance). | Audited for open educational redistribution, zero PII, and clean application-time features (resolves O-001). See `docs/data/DATASET_AUDIT.md`. |
| D-022 | Target variable is `Loan_Status` (binary: 1 = Approved, 0 = Rejected). | Represents origination underwriting outcome; observed historical ratio ~69% approved / ~31% rejected (resolves O-002). |
| D-023 | Model input schema finalized to 9 features; sensitive attributes (`Gender`, `Married`) excluded for Fair Lending. | Complies with Equal Credit Opportunity Act (ECOA) standards against demographic proxy bias; all 9 features known at application time (resolves O-003). |

## 2. Proposed decisions needing validation

| ID | Proposal | Why not final |
|---|---|---|
| P-001 | Use Docker Compose for local multi-service development. | Confirm it is useful and practical for the selected stack and local environment. |
| P-002 | Use `/api/v1` for public backend routes. | API versioning convention has not been approved. |
| P-003 | Use a migration tool such as Alembic. | Choose when database/ORM details are finalized. |
| P-004 | Use UUID identifiers for database records. | Candidate, not yet approved. |
| P-005 | Use a common JSON error envelope and request correlation IDs. | Shape and status mapping still need approval. |
| P-006 | Restrict ML calls through private networking or service-to-service authentication. | Exact mechanism depends on Render service topology and plan. |

## 3. Open decisions

| ID | Question | Status | Needed by |
|---|---|---|---|
| O-001 | Which dataset is suitable, licensed, and available for this task? | **Resolved by D-021** | Phase 2 |
| O-002 | What exactly does the target label represent, and how reliable is it? | **Resolved by D-022** | Phase 2 |
| O-003 | What fields are available, meaningful, and permitted as model inputs? | **Resolved by D-023** | Phase 2 |
| O-004 | Which evaluation metrics and acceptance thresholds are defensible? | Open | Phase 3 |
| O-005 | Which model and preprocessing pipeline should be selected? | Open | Phase 3 |
| O-006 | Which explanation technique is suitable for the selected model? | Open | Phase 3 |
| O-007 | Is a probability score valid and appropriately calibrated for display? | Open | Phase 3 |
| O-008 | Cookie-based sessions or JWT access/refresh tokens? | Open | Before auth implementation |
| O-009 | Is email verification/password reset in the MVP? | Open | Before auth implementation |
| O-010 | What admin operations and permissions are needed? | Open | Before admin implementation |
| O-011 | What is the account deletion, prediction retention, and audit policy? | Open | Before database implementation |
| O-012 | What database ORM and migration tool will be used? | Open | Before database implementation |
| O-013 | What is the backend-to-ML service authentication/network design? | Open | Before deployment |
| O-014 | Is Render suitable for the ML service given model size, memory, startup, and cost? | Open | Before deployment |
| O-015 | What performance, availability, and rate-limit targets should be set? | Open | Before release |
| O-016 | What is the model artifact storage, release, rollback, and retraining process? | Open | Before production deployment |

## 4. Decision change policy

- Do not silently replace a confirmed decision.
- If new evidence requires a change, document the proposed change, rationale, impact, and affected documents.
- Keep dataset-dependent decisions provisional until the audit is complete.
- Update the PRD, SRS, architecture, API contract, database design, and this register when a decision changes.
- Antigravity must report assumptions and unresolved decisions instead of inventing values or silently expanding scope.
