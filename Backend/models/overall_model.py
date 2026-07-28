from typing import Dict, Optional
from pydantic import BaseModel


class LoanDecisionResponse(BaseModel):
    overall_score: Optional[int] = None
    approval_probability: Optional[int] = None
    decision: Optional[str] = None
    summary: Optional[str] = None
    document_scores: Dict[str, int]