from typing import List, Optional
from pydantic import BaseModel, Field


class CheckResult(BaseModel):
    score: Optional[int] = Field(default=None, ge=0, le=100)
    issues: Optional[List[str]] = None


class Checks(BaseModel):
    font: Optional[CheckResult] = None
    layout: Optional[CheckResult] = None
    template: Optional[CheckResult] = None
    tampering: Optional[CheckResult] = None


class RiskResponse(BaseModel):
    overall_score: Optional[int] = Field(default=None, ge=0, le=100)
    authenticity_score: Optional[int] = Field(default=None, ge=0, le=100)
    status: Optional[str] = None
    summary: Optional[str] = None
    checks: Optional[Checks] = None