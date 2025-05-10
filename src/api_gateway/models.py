from pydantic import BaseModel, Field, validator, constr
from typing import List, Optional, Dict, Annotated
from datetime import datetime
import re

class ProblemStatement(BaseModel):
    """Model for problem statement validation request."""
    title: Annotated[str, Field(min_length=10, max_length=200)] = Field(
        ..., 
        description="Title of the problem statement"
    )
    description: Annotated[str, Field(min_length=50, max_length=2000)] = Field(
        ..., 
        description="Detailed description of the problem"
    )
    keywords: List[str] = Field(
        ..., 
        description="Keywords for searching relevant discussions",
        min_items=1,
        max_items=10
    )
    target_market: Optional[Annotated[str, Field(min_length=3, max_length=100)]] = Field(
        None, 
        description="Target market or audience"
    )
    industry: Optional[str] = Field(
        None,
        description="Industry sector the problem belongs to"
    )
    
    @validator('keywords')
    def validate_keywords(cls, v):
        """Validate that keywords are properly formatted."""
        for keyword in v:
            if len(keyword) < 2 or len(keyword) > 50:
                raise ValueError(
                    f'Keyword "{keyword}" must be between 2 and 50 characters'
                )
            if not re.match(r'^[a-zA-Z0-9\s\-]+$', keyword):
                raise ValueError(
                    f'Keyword "{keyword}" contains invalid characters. '
                    'Only letters, numbers, spaces, and hyphens are allowed.'
                )
        return v
    
    @validator('description')
    def validate_description(cls, v):
        """Validate that description is meaningful."""
        if len(v.split()) < 10:
            raise ValueError(
                'Description must contain at least 10 words'
            )
        return v

class ValidationResult(BaseModel):
    """Model for problem validation results."""
    problem_id: str = Field(..., description="Unique identifier for the validated problem")
    timestamp: datetime = Field(..., description="Time when validation was completed")
    sentiment_summary: Dict = Field(..., description="Summary of sentiment analysis results")
    engagement_metrics: Dict = Field(..., description="Metrics about user engagement")
    temporal_analysis: Dict = Field(..., description="Analysis of temporal distribution")
    validation_score: float = Field(
        ..., 
        description="Overall validation score",
        ge=0.0,
        le=1.0
    )
    relevant_posts: List[Dict] = Field(
        ..., 
        description="List of relevant posts found during validation",
        min_items=0
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ValidationRequest(BaseModel):
    """Model for validation request status."""
    request_id: str = Field(..., description="Unique identifier for the validation request")
    status: str = Field(
        ..., 
        description="Current status of the validation request",
        regex='^(pending|processing|completed|failed)$'
    )
    created_at: datetime = Field(..., description="Time when request was created")
    completed_at: Optional[datetime] = Field(None, description="Time when validation completed")
    result: Optional[ValidationResult] = Field(None, description="Validation results if completed")
    error: Optional[str] = Field(None, description="Error message if validation failed")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
