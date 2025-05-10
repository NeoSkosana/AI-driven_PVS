"""Models for the API gateway."""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime

class ValidationRequest(BaseModel):
    """Model for problem validation request."""
    title: str = Field(
        ...,
        min_length=10,
        max_length=200,
        description="Title of the problem statement"
    )
    description: str = Field(
        ...,
        min_length=50,
        max_length=2000,
        description="Detailed description of the problem"
    )
    keywords: List[str] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="List of relevant keywords for the problem"
    )
    target_market: Optional[str] = Field(
        None,
        max_length=200,
        description="Target market or audience for the solution"
    )

    @validator('keywords')
    def validate_keywords(cls, v):
        """Validate keywords are properly formatted."""
        if not all(2 <= len(k.strip()) <= 50 for k in v):
            raise ValueError("Keywords must be between 2 and 50 characters")
        return [k.strip().lower() for k in v]

class ValidationResponse(BaseModel):
    """Model for validation response."""
    request_id: str = Field(
        ...,
        description="Unique identifier for the validation request"
    )
    status: str = Field(
        ...,
        description="Status of the validation request"
    )
    
class ValidationResult(BaseModel):
    """Model for validation results."""
    problem_id: str = Field(
        ...,
        description="Unique identifier for the validation request"
    )
    sentiment_summary: Dict[str, Any] = Field(
        ...,
        description="Summary of sentiment analysis results"
    )
    engagement_metrics: Dict[str, Any] = Field(
        ...,
        description="Metrics about user engagement"
    )
    temporal_analysis: Dict[str, Any] = Field(
        ...,
        description="Analysis of posting patterns over time"
    )
    validation_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall validation score between 0 and 1"
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in the validation results between 0 and 1"
    )
    validation_flags: List[str] = Field(
        default_factory=list,
        description="List of flags indicating potential issues with validation"
    )

    class Config:
        schema_extra = {
            "example": {
                "sentiment_summary": {
                    "overall_sentiment": "POSITIVE",
                    "positive_ratio": 0.7,
                    "negative_ratio": 0.1,
                    "neutral_ratio": 0.2,
                    "average_score": 0.75,
                    "weighted_average_score": 0.82
                },
                "engagement_metrics": {
                    "avg_score": 45.5,
                    "avg_comments": 8.2,
                    "total_engagement": 324,
                    "unique_users": 156
                },
                "temporal_analysis": {
                    "earliest_post": "2025-01-01T00:00:00Z",
                    "latest_post": "2025-05-10T00:00:00Z",
                    "avg_posts_per_day": 3.5,
                    "activity_period_days": 130
                },
                "validation_score": 0.85,
                "confidence_score": 0.92,
                "validation_flags": []
            }
        }
