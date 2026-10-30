# SmartLoan Predictor — Planning & Data Architecture Baseline

This package contains planning baselines and architectural specifications for SmartLoan Predictor, maintained through phased milestones.

## Contents

- `PRD.md` — product scope, personas, and acceptance criteria
- `SRS.md` — functional/non-functional requirements and data validation specs
- `SYSTEM_ARCHITECTURE.md` — service responsibilities and decoupled request flows
- `API_CONTRACT.md` — service endpoints, error envelopes, and finalized 9-feature prediction payload
- `DATABASE_DESIGN.md` — conceptual PostgreSQL design and JSONB input snapshot specification
- `DECISION_REGISTER.md` — living register of confirmed choices (`D-001`–`D-023`), proposals, and open decisions
- `ANTIGRAVITY_HANDOFF_PROMPT.md` — operating rules and guardrails for Google Antigravity
- `../data/DATASET_AUDIT.md` — Phase 2 Data Card, provenance, target semantics, leakage audit, and 9-feature dictionary

## Status and Phase Alignment

- **Phase 1 (Planning Baseline):** Complete (v0.1.0).
- **Phase 2 (Dataset Selection, Audit, and Licensing):** Complete (v0.2.0). Dataset, target label semantics (`Loan_Status`), Fair Lending exclusions (`Gender`/`Married`), and 9-feature input schema are formally approved.
- **Phase 3 (ML Modeling & Calibration):** Upcoming. Model algorithm, probability calibration, and packaging remain to be implemented.
