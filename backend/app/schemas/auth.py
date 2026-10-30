"""Credix Backend — Authentication Schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Registration request payload."""
    email: EmailStr = Field(..., description="Valid applicant email address")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")


class UserLogin(BaseModel):
    """Login request payload."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Public user profile schema."""
    id: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """JWT bearer token response."""
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str


class TokenPayload(BaseModel):
    """Decoded JWT payload data."""
    sub: Optional[str] = None
    role: Optional[str] = None
