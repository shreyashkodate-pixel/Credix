"""Credix Backend — Prediction Schemas matching API_CONTRACT.md."""

from datetime import datetime
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, ConfigDict, Field, model_validator


class PredictionCreateRequest(BaseModel):
    """9-feature applicant prediction submission payload."""

    applicant_income: float = Field(..., gt=0.0, description="Gross monthly income of primary applicant")
    coapplicant_income: float = Field(default=0.0, ge=0.0, description="Gross monthly income of co-applicant")
    loan_amount: float = Field(..., gt=0.0, description="Loan amount requested in thousands ($1,000s)")
    loan_amount_term: int = Field(..., description="Duration of loan in months")
    credit_history: Literal[0, 1] = Field(..., description="Credit guidelines flag (1=meets, 0=does not)")
    education: Literal["Graduate", "Not Graduate"] = Field(..., description="Highest completed education")
    self_employed: Literal["Yes", "No"] = Field(..., description="Self employment status")
    dependents: Literal["0", "1", "2", "3+"] = Field(..., description="Number of dependents")
    property_area: Literal["Urban", "Semiurban", "Rural"] = Field(..., description="Property geographic zone")

    @model_validator(mode="before")
    @classmethod
    def check_prohibited_demographics(cls, data: Any) -> Any:
        if isinstance(data, dict):
            prohibited = ["gender", "married", "race", "sex"]
            for key in prohibited:
                if key in data:
                    raise ValueError(
                        f"Prohibited demographic attribute '{key}' detected. "
                        "Fair Lending policy strictly excludes demographic data from model input."
                    )
        return data

    @model_validator(mode="after")
    def validate_loan_term(self) -> "PredictionCreateRequest":
        allowed_terms = [12, 36, 60, 120, 180, 240, 300, 360, 480]
        if self.loan_amount_term not in allowed_terms:
            raise ValueError(f"loan_amount_term must be one of {allowed_terms}, got {self.loan_amount_term}")
        return self


class PredictionFactor(BaseModel):
    """Local attribution factor produced by TreeSHAP."""
    factor: str
    impact: Literal["positive", "negative"]
    weight: float
    description: str


class PredictionExplanation(BaseModel):
    """Structured explanation object."""
    method: str = "TreeSHAP"
    factors: List[PredictionFactor] = []


class PredictionResponse(BaseModel):
    """Prediction outcome returned to client."""
    prediction_id: str
    outcome: Literal["Approved", "Rejected"]
    probability: Optional[float] = None
    model_version: str
    created_at: datetime
    explanation: PredictionExplanation


class PredictionHistoryItem(BaseModel):
    """Single historical prediction record."""
    id: str
    created_at: datetime
    model_version: str
    outcome: str
    probability: Optional[float] = None
    explanation: Dict[str, Any]
    input_snapshot: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class PredictionHistoryPage(BaseModel):
    """Bounded paginated user prediction history envelope."""
    items: List[PredictionHistoryItem]
    total: int
    page: int
    page_size: int
