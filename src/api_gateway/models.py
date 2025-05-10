from pydantic import BaseModel, Field, validator, constr
from typing import List, Optional, Dict, Annotated
from datetime import datetime
import re

class ProblemStatement(BaseModel):
    """Model for problem statement validation request."""
    title: Annotated[str, Field(min_length=10, max_length=200)] = Field(
        ..., 
        description="Title of the problem statement",
        example="AI-Powered Personal Finance Management App for Gen Z"
    )
    description: Annotated[str, Field(min_length=50, max_length=2000)] = Field(
        ..., 
        description="Detailed description of the problem and proposed solution",
        example="""
        Young adults (Gen Z) struggle with financial literacy and managing their finances effectively.
        Our AI-powered app will provide personalized financial advice, automate savings, and gamify 
        financial education to make it more engaging and accessible for the Gen Z audience.
        """
    )
    keywords: List[str] = Field(
        ..., 
        description="Keywords for searching relevant discussions. Use specific terms related to your problem domain.",
        min_items=1,
        max_items=10,
        example=["personal finance", "Gen Z", "financial literacy", "fintech", "banking app"]
    )
    target_audience: str = Field(
        ...,
        description="Primary target audience for the solution",
        example="Generation Z (ages 18-25)"
    )
    industry: str = Field(
        ...,
        description="Industry or sector the problem belongs to",
        example="Fintech"
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

    class Config:
        schema_extra = {
            "description": "A model representing a problem statement for validation",
            "example": {
                "title": "AI-Powered Personal Finance Management App for Gen Z",
                "description": "Young adults (Gen Z) struggle with financial literacy...",
                "keywords": ["personal finance", "Gen Z", "financial literacy", "fintech", "banking app"],
                "target_audience": "Generation Z (ages 18-25)",
                "industry": "Fintech"
            }
        }

class ValidationResult(BaseModel):
    """Model representing the results of problem validation analysis."""
    problem_id: str = Field(
        ...,
        description="Unique identifier for the validation request",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    status: str = Field(
        ...,
        description="Current status of the validation request",
        example="completed"
    )
    sentiment_score: Optional[float] = Field(
        None,
        description="Overall sentiment score from -1 (negative) to 1 (positive)",
        example=0.75,
        ge=-1,
        le=1
    )
    engagement_metrics: Dict[str, int] = Field(
        ...,
        description="Metrics showing engagement levels in discussions",
        example={
            "total_discussions": 150,
            "total_comments": 450,
            "unique_users": 320
        }
    )
    key_insights: List[str] = Field(
        ...,
        description="Main insights extracted from the analysis",
        example=[
            "Strong demand for simplified financial education",
            "Users prefer gamified learning experiences",
            "Privacy concerns are a major consideration"
        ]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the validation request was created",
        example="2025-05-10T12:00:00Z"
    )
    completed_at: Optional[datetime] = Field(
        None,
        description="Timestamp when the validation was completed",
        example="2025-05-10T12:05:30Z"
    )

    class Config:
        schema_extra = {
            "description": "Results from the problem validation analysis",
            "example": {
                "problem_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "completed",
                "sentiment_score": 0.75,
                "engagement_metrics": {
                    "total_discussions": 150,
                    "total_comments": 450,
                    "unique_users": 320
                },
                "key_insights": [
                    "Strong demand for simplified financial education",
                    "Users prefer gamified learning experiences",
                    "Privacy concerns are a major consideration"
                ],
                "created_at": "2025-05-10T12:00:00Z",
                "completed_at": "2025-05-10T12:05:30Z"
            }
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
