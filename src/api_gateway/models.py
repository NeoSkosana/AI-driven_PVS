from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ProblemStatement(BaseModel):
    """Model for problem statement validation request."""
    title: str = Field(..., description="Title of the problem statement")
    description: str = Field(..., description="Detailed description of the problem")
    keywords: List[str] = Field(..., description="Keywords for searching relevant discussions")
    target_market: Optional[str] = Field(None, description="Target market or audience")
    
class ValidationResult(BaseModel):
    """Model for problem validation results."""
    problem_id: str
    timestamp: datetime
    sentiment_summary: dict
    engagement_metrics: dict
    temporal_analysis: dict
    validation_score: float
    relevant_posts: List[dict]
    
class ValidationRequest(BaseModel):
    """Model for validation request status."""
    request_id: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[ValidationResult] = None
