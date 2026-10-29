# Antigravity Handoff — SmartLoan Predictor Phase 1 Documentation

Use this prompt in Google Antigravity after placing the `docs/planning/` files in the SmartLoan Predictor repository.

---

You are working on the SmartLoan Predictor repository. Your task is to review and integrate the provided Phase 1 planning documents, not to implement application code.

## Scope
1. Inspect the current repository and existing files before making changes.
2. Review all six documents in `docs/planning/`:
   - `PRD.md`
   - `SRS.md`
   - `SYSTEM_ARCHITECTURE.md`
   - `API_CONTRACT.md`
   - `DATABASE_DESIGN.md`
   - `DECISION_REGISTER.md`
3. Preserve the agreed stack and deployment choices:
   - Frontend: Next.js + TypeScript, Vercel
   - Backend API: Python + FastAPI, Render
   - ML service: Python + FastAPI/scikit-learn, likely Render but tentative
   - Database: PostgreSQL on Supabase
   - Google Antigravity is the coding IDE/agent
4. Check consistency between the documents. Report contradictions, duplication, missing decisions, and assumptions that need user approval.
5. Make only documentation edits needed to improve consistency, clarity, and traceability. Do not create application source code, install packages, train a model, download a dataset, provision services, connect to production, or create secrets.
6. Do not invent a dataset, target label, final model input fields, model algorithm, probability calibration, authentication strategy, data-retention policy, performance target, or hosting capability. Keep these as explicit open decisions until supported.
7. Do not delete or overwrite existing project work. If the repository already has similarly named documents, compare them first and report the safest merge/update plan before replacing content.
8. Do not commit or push changes unless explicitly instructed.

## Verification
- Check that each document has a clear status and version.
- Check that decisions marked confirmed match across all documents.
- Check that tentative and unresolved items are clearly marked.
- Check that the prediction flow does not allow the frontend to call the ML service/database directly.
- Check that user history is ownership-scoped by the authenticated identity.
- Check that probabilities are not promised unless validated.
- Check that failed inference cannot be reported as a successful saved prediction.
- Provide a concise report with files inspected/changed, consistency findings, remaining decisions, and verification performed.

First report the repository state and proposed changes. Then make only safe documentation changes within the scope above.
