# Credix (SmartLoan Predictor)

Credix is an AI/ML-assisted loan outcome prediction web application designed to demonstrate an end-to-end, portfolio-quality software architecture. The platform enables registered users to submit loan-related applicant data, receive model-generated outcome predictions accompanied by clear explanatory factors, and inspect their personal prediction history with strict ownership controls.

---

## Important Purpose and Limitations

- **Educational & Portfolio Scope**: Credix is built for technical demonstration and educational purposes.
- **No Lending Decisions**: It does not submit real loan applications, does not make legally binding lending decisions, and does not serve as a substitute for professional underwriting or financial advice.
- **Explainability, Not Causation**: Explanations highlight feature associations learned by the model; they are not proof of causal relationships.
- **Probability Policy**: Predicted probabilities are withheld unless model calibration and rigorous validation justify displaying them.

---

## Planned Technology Stack and Hosting

| Service Layer | Planned Technology | Hosting / Deployment | Status |
|---|---|---|---|
| **Frontend** | Next.js, TypeScript, Tailwind CSS | Vercel | Confirmed |
| **Backend API** | Python, FastAPI, Pydantic | Render | Confirmed |
| **ML Inference Service** | Python, FastAPI, scikit-learn | Render | Tentative (pending memory & cold-start evaluation) |
| **Database** | PostgreSQL | Supabase | Confirmed |
| **Development Agent** | Google Antigravity | Local / Git | Confirmed |

*Note: The ML inference service provider is tentative pending evaluation of memory limits, cold-start behavior, and network isolation on Render.*

---

## Current Project Status and Roadmap

The project is currently at the completion of **Phase 1 (Documentation and Planning Baseline)**. 

> **Important**: Application source code, dataset acquisition, and model training **have not started**.

### Phased Roadmap

1. **Phase 1: Planning and Requirements** *(Current — Baseline Approved, v0.1.0)*
   - PRD, SRS, architecture, API contracts, database design, and decision register established.
2. **Phase 2: Dataset Selection, Audit, and Licensing** *(Upcoming)*
   - Identify appropriately licensed loan dataset, audit target label definitions, and finalize input feature schema.
3. **Phase 3: ML Modeling, Pipeline, and Calibration**
   - Reproducible preprocessing, baseline training, evaluation, explainability method, and artifact packaging.
4. **Phase 4: Backend API and Database Implementation**
   - Supabase schema migrations, authentication, authorization, and ML service orchestration.
5. **Phase 5: Frontend UI and Integration**
   - Responsive user interface, prediction workflows, history dashboard, and admin views.
6. **Phase 6: Verification, Hardening, and Deployment**
   - Automated testing, security checks, end-to-end verification, and live cloud deployments.

---

## Project Tracking

- [`progress.md`](progress.md) — Current sprint/phase progress, completed deliverables, and next-session agenda.
- [`technical_debt.md`](technical_debt.md) — Living register of deferred architectural choices, provisional items, and risks.

---

## Planning Documentation

Detailed specifications and architectural baselines are maintained under [`docs/planning/`](docs/planning/):

- [`docs/planning/README.md`](docs/planning/README.md) — Overview of planning documents and status caveats.
- [`docs/planning/PRD.md`](docs/planning/PRD.md) — Product Requirements Document (goals, personas, scope).
- [`docs/planning/SRS.md`](docs/planning/SRS.md) — Software Requirements Specification (functional & non-functional requirements).
- [`docs/planning/SYSTEM_ARCHITECTURE.md`](docs/planning/SYSTEM_ARCHITECTURE.md) — Multi-service architecture and request flows.
- [`docs/planning/API_CONTRACT.md`](docs/planning/API_CONTRACT.md) — Proposed endpoint contracts and payload formats.
- [`docs/planning/DATABASE_DESIGN.md`](docs/planning/DATABASE_DESIGN.md) — Conceptual PostgreSQL data model and indexing strategy.
- [`docs/planning/DECISION_REGISTER.md`](docs/planning/DECISION_REGISTER.md) — Confirmed choices, proposals, and open decisions.
- [`docs/planning/ANTIGRAVITY_HANDOFF_PROMPT.md`](docs/planning/ANTIGRAVITY_HANDOFF_PROMPT.md) — Guidelines and guardrails for Google Antigravity.

---

## Security Guidance

- **Never Commit Secrets**: Do not commit real passwords, API keys, database credentials, or secret tokens to version control.
- **Environment Variables**: Use `.env.example` as a template for required variables. Store all active runtime credentials in untracked `.env` files or platform secret managers.
- **No Direct Database Access**: Browser clients must never connect directly to Supabase or the ML inference service. All communication flows through the authenticated Backend API.

