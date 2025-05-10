import uuid
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, status, Request
from datetime import datetime
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from functools import partial

from .models import ProblemStatement, ValidationResult, ValidationRequest
from ..data_collection.reddit_collector import RedditCollector
from ..analyzer.sentiment_analyzer import SentimentAnalyzer
from ..storage_service.mongodb_storage import StorageService
from ..cache.redis_cache import RedisCache
from ..queue.message_queue import MessageQueue
from ..auth.auth_service import get_current_active_user, User
from ..middleware.rate_limiter import RateLimiter
from ..utils.error_handlers import (
    AppException,
    ValidationException,
    app_exception_handler,
    validation_exception_handler
)

app = FastAPI(
    title="Problem Validation API",
    description="API for validating micro-SaaS business problems using Reddit data analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(ValidationException, validation_exception_handler)

# Initialize services
reddit_collector = RedditCollector()
sentiment_analyzer = SentimentAnalyzer()
storage_service = StorageService()
cache_service = RedisCache()
message_queue = MessageQueue()
rate_limiter = RateLimiter(cache_service)

# Ensure message queue connection
message_queue.connect()
message_queue.declare_queue("validation_tasks")

# Store background tasks
active_validations = {}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def check_rate_limit(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """Dependency for rate limiting."""
    await rate_limiter.check_rate_limit(request, current_user.username)
    return current_user

# Use this instead of get_current_active_user in the endpoints
rate_limited_user = partial(check_rate_limit)

def process_validation_task(message: dict):
    """Process a validation task from the message queue."""
    try:
        problem_id = message.get("problem_id")
        problem = message.get("problem")

        if not problem_id or not problem:
            raise ValidationException("Invalid message format")

        # Update status to processing
        validation_request = active_validations.get(problem_id)
        if validation_request:
            validation_request.status = "processing"

        # Collect data from Reddit
        posts = reddit_collector.collect_posts(
            subreddit_name="startups",  # Could be configurable
            keywords=problem["keywords"],
            time_filter="year",
            limit=100
        )

        # Analyze collected data
        analysis_result = sentiment_analyzer.analyze_problem_validation(posts)

        # Create validation result
        result = ValidationResult(
            problem_id=problem_id,
            timestamp=datetime.utcnow(),
            sentiment_summary=analysis_result["sentiment_summary"],
            engagement_metrics=analysis_result["engagement_metrics"],
            temporal_analysis=analysis_result["temporal_analysis"],
            validation_score=analysis_result["validation_score"],
            relevant_posts=posts
        )

        # Store result
        storage_service.store_validation_result(problem_id, result.dict())

        # Update request status
        if validation_request:
            validation_request.status = "completed"
            validation_request.completed_at = datetime.utcnow()
            validation_request.result = result

    except Exception as e:
        # Handle errors
        if validation_request:
            validation_request.status = "failed"
            validation_request.error = str(e)
        raise

# Start consuming validation tasks
message_queue.channel.basic_consume(
    queue="validation_tasks",
    on_message_callback=lambda ch, method, props, body: process_validation_task(body)
)

@app.post("/validate", response_model=ValidationRequest)
async def validate_problem(
    problem: ProblemStatement,
    current_user: User = Depends(rate_limited_user)
) -> ValidationRequest:
    """Submit a problem statement for validation."""
    try:
        problem_id = str(uuid.uuid4())
        
        # Create validation request
        validation_request = ValidationRequest(
            request_id=problem_id,
            status="pending",
            created_at=datetime.utcnow()
        )
        
        # Store request
        active_validations[problem_id] = validation_request
        
        # Queue validation task
        message_queue.publish(
            "validation_tasks",
            {
                "problem_id": problem_id,
                "problem": problem.dict()
            }
        )
        
        return validation_request
    except Exception as e:
        raise ValidationException(str(e))

@app.get("/validate/{problem_id}", response_model=ValidationRequest)
async def get_validation_status(
    problem_id: str,
    current_user: User = Depends(rate_limited_user)
) -> ValidationRequest:
    """Get the status of a problem validation request."""
    validation_request = active_validations.get(problem_id)
    if not validation_request:
        # Try to load from storage
        stored_result = storage_service.get_validation_result(problem_id)
        if stored_result:
            return ValidationRequest(
                request_id=problem_id,
                status="completed",
                created_at=stored_result["timestamp"],
                completed_at=stored_result["timestamp"],
                result=ValidationResult(**stored_result)
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Validation request {problem_id} not found"
        )
    return validation_request

@app.get("/problems", response_model=List[ValidationResult])
async def list_problems(
    limit: int = 100,
    current_user: User = Depends(rate_limited_user)
) -> List[ValidationResult]:
    """List all validated problems."""
    try:
        results = storage_service.get_all_validation_results(limit=limit)
        return [ValidationResult(**result) for result in results]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.delete("/problems/{problem_id}")
async def delete_problem(
    problem_id: str,
    current_user: User = Depends(rate_limited_user)
) -> dict:
    """Delete a validated problem and its results."""
    try:
        storage_service.delete_validation_result(problem_id)
        if problem_id in active_validations:
            del active_validations[problem_id]
        return {"message": f"Problem {problem_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
