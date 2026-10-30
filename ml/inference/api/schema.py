"""Pydantic schemas for Credix ML inference service API contracts."""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    """Audited 9-feature model input contract matching API_CONTRACT.md."""
    applicant_income: float = Field(..., gt=0.0, description="Gross monthly income of primary applicant")
    coapplicant_income: float = Field(default=0.0, ge=0.0, description="Gross monthly income of co-applicant")
    loan_amount: float = Field(..., gt=0.0, description="Loan amount in thousands ($1,000s)")
    loan_amount_term: int = Field(..., description="Duration of loan in months (e.g. 120, 180, 240, 360)")
    credit_history: Literal[0, 1] = Field(..., description="Credit guidelines flag (1=meets, 0=does not)")
    education: Literal["Graduate", "Not Graduate"] = Field(..., description="Highest completed education")
    self_employed: Literal["Yes", "No"] = Field(..., description="Self employment status")
    dependents: Literal["0", "1", "2", "3+"] = Field(..., description="Number of dependents")
    property_area: Literal["Urban", "Semiurban", "Rural"] = Field(..., description="Property geographic zone")


class FactorItem(BaseModel):
    """Local attribution factor produced by TreeSHAP."""
    factor: str
    impact: Literal["positive", "negative"]
    weight: float
    description: str


class ExplanationResponse(BaseModel):
    """Structured explanation object."""
    method: str = "TreeSHAP"
    factors: List[FactorItem] = []


class PredictionResponse(BaseModel):
    """Inference output schema matching API_CONTRACT.md."""
    outcome: Literal["Approved", "Rejected"]
    raw_class: int
    probability: float
    model_version: str
    algorithm: str
    explanation: ExplanationResponse


class HealthResponse(BaseModel):
    """Liveness & readiness probe response."""
    status: str = "ok"
    model_ready: bool
    model_version: Optional[str] = None

