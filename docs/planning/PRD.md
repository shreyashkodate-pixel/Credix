# SmartLoan Predictor — Product Requirements Document (PRD)

**Document status:** Draft for review  
**Version:** 0.1.0  
**Phase:** 1 — Planning and Requirements  
**Product name:** SmartLoan Predictor

## 1. Product overview

SmartLoan Predictor is a portfolio-quality web application that demonstrates an AI/ML-assisted loan outcome prediction workflow. A registered user provides applicant and loan-related information, receives a model-generated outcome prediction with a clear explanation of relevant factors, and can review their own previous predictions. Administrators have a separate, permission-controlled view for operational oversight.

The system is an educational and portfolio project. Unless later supported by appropriate data, validation, legal review, and governance, it must not be presented as a production-ready lending decision system or as a substitute for a lender's underwriting process.

## 2. Problem statement

Loan eligibility datasets and ML demonstrations are often presented as isolated notebooks or simple forms. This project aims to demonstrate a complete, documented software system: user-facing interface, authenticated API, independently deployable inference service, persistent history, administration, tests, and online deployment.

## 3. Goals

1. Build a modern, responsive web application suitable for a technical portfolio.
2. Demonstrate an end-to-end ML prediction workflow using a documented and appropriately licensed dataset.
3. Separate UI, business logic/data access, and model inference into clear service boundaries.
4. Support registered-user accounts and role-based administrative access.
5. Explain model outputs in language users can understand, without claiming causal or underwriting certainty.
6. Preserve a user's prediction history with strict ownership controls.
7. Include reproducible training/inference artifacts, automated tests, operational health checks, and deployment documentation.
8. Use Google Antigravity as the primary coding IDE/AI development agent, with human review and verification at each phase.

## 4. Non-goals and limitations

- The application will not submit real loan applications to banks or lenders.
- It will not make legally binding lending decisions.
- It will not promise approval, guarantee eligibility, or imply that model outputs are professional financial advice.
- It will not collect real financial documents, bank credentials, government identifiers, or other unnecessary sensitive information for the initial portfolio version.
- It will not claim calibrated probability estimates unless calibration and evaluation support that interpretation.
- It will not claim that feature explanations are causal explanations.
- It will not train on a dataset until source, license, target definition, data quality, and suitability have been audited.
- It will not expose database credentials, model-service secrets, or privileged admin operations to the browser.

## 5. Intended users

### 5.1 Registered user
- Registers and signs in.
- Submits the supported input fields.
- Receives the model's predicted class/outcome and a suitable explanation.
- Views their own prior prediction records.
- Signs out and can request account/data deletion according to the final policy.

### 5.2 Administrator
- Signs in with an authorized administrator role.
- Views aggregated operational metrics and permitted records.
- Manages user access where specified by the approved requirements.
- Reviews appropriate audit events.
- Does not receive unrestricted access to passwords, authentication secrets, or unnecessary private user data.

## 6. Product scope and principal capabilities

1. **Authentication and accounts:** registration, sign-in, sign-out, current-user profile, secure password handling or an approved equivalent.
2. **Role-based access:** regular user and administrator roles enforced by the backend, not just by hiding frontend controls.
3. **Prediction form:** fields will be finalized only after the dataset audit. Client-side convenience validation must be repeated server-side.
4. **Prediction workflow:** backend validates and authorizes the request, invokes the ML service, records a successful result, and returns a stable response.
5. **Explanation:** show the supported factors that influenced the model output. Explain limitations and avoid causal language.
6. **History:** users can access only their own records. Admin access is explicitly permissioned and audited as appropriate.
7. **Admin dashboard:** aggregate statistics and user/record management within approved authorization boundaries.
8. **Operational behavior:** health/readiness checks, structured error responses, safe logging, service timeouts, and no successful history record when inference fails.
9. **Testing and quality:** unit, integration, API contract, authorization, and end-to-end tests as appropriate.
10. **Deployment:** public frontend on Vercel; backend API on Render; ML service likely on Render (tentative); PostgreSQL on Supabase.

## 7. User experience principles

- Modern, clear, responsive interface with accessible labels, validation messages, keyboard navigation, and appropriate loading/empty/error states.
- Results distinguish model output from facts about a real lender's decision.
- Use plain language for explanations and disclose important limitations.
- Avoid manipulative or overly confident wording.
- Do not show a numeric probability as if it were reliable unless model validation and calibration justify it.

## 8. High-level user journeys

### Registered user prediction
1. User registers or signs in.
2. User opens the prediction form.
3. User submits required fields.
4. Frontend sends the request to the backend over HTTPS.
5. Backend authenticates the user and validates the request.
6. Backend calls the private ML service.
7. ML service returns a versioned prediction and supported explanation.
8. Backend stores the successful prediction in PostgreSQL.
9. Backend returns the result; frontend renders it.
10. User can revisit the result in personal history.

If inference or persistence fails, the system returns a safe error and must not report an unpersisted prediction as a completed, saved result. Exact transaction and retry behavior will be specified during implementation.

### Administrator oversight
1. An authorized administrator signs in.
2. Backend checks the administrator role for each protected operation.
3. Dashboard displays permitted aggregate metrics.
4. Administrative user/record operations are validated and audited where required.

## 9. Success criteria

The project can be considered portfolio-ready when:
- requirements and architecture are documented and version-controlled;
- dataset provenance, license, target, limitations, and evaluation are documented;
- model training and inference are reproducible and use the same preprocessing;
- core user journeys work in a deployed environment;
- role-based access and history ownership are covered by automated tests;
- model/service failures are handled safely;
- secrets are not committed or exposed in browser bundles;
- automated checks pass and known limitations are documented;
- deployment and local setup instructions are reproducible.

Quantitative performance, availability, and model-quality thresholds remain open until the dataset and deployment constraints are understood.

## 10. Proposed release scope

### Initial release (MVP)
- Registration/sign-in/sign-out
- User and administrator roles
- Dataset-backed prediction form
- Prediction result and appropriately qualified explanation
- Private prediction history
- Basic admin dashboard and approved user management
- PostgreSQL persistence
- Automated tests, health checks, deployment, and documentation

### Possible later enhancements (not committed)
- Model monitoring and drift reports
- Controlled retraining pipeline
- More advanced explanations such as SHAP, if appropriate and validated
- Account export/deletion automation
- Additional datasets or model comparisons
- More comprehensive audit/reporting features

## 11. Constraints and assumptions

- Google Antigravity is the primary coding IDE and AI development agent.
- The user currently has no confirmed dataset, trained model, or source code for this project.
- The dataset and its license have not yet been selected or audited.
- Frontend: Next.js + TypeScript, hosted on Vercel.
- Backend API: Python + FastAPI, hosted on Render.
- ML service: Python + FastAPI, likely hosted on Render; provider is not final.
- Database: PostgreSQL on Supabase.
- Git and GitHub will be used for version control.
- Docker Compose is proposed for local multi-service development, subject to confirming a practical setup.
- Exact authentication mechanism, data retention, service-to-service authentication, model algorithm, and probability approach are unresolved.

## 12. Open questions

1. Which dataset is legally usable and appropriate for the intended prediction task?
2. What does the target label mean in the source data, and is it a defensible proxy for the intended outcome?
3. Which input fields are available at inference time and permitted for use?
4. What evaluation metrics and minimum thresholds are appropriate?
5. Which authentication strategy should be used?
6. What data deletion and retention rules are required?
7. Which explanation method fits the final model and data?
8. Can the ML service comfortably run on the selected Render plan, considering startup time, memory, and cold starts?
9. What are the service-level performance and availability targets?

## 13. Acceptance checklist

- [ ] Stakeholder reviews goals, users, scope, and non-goals.
- [ ] Dataset-dependent claims remain explicitly provisional.
- [ ] No undocumented promise of real-world loan approval accuracy.
- [ ] Architecture and hosting choices match the current decision register.
- [ ] Open questions are tracked rather than silently guessed.
