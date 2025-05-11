import uuid
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.openapi.utils import get_openapi
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
from ..middleware.monitoring_middleware import MonitoringMiddleware
from ..utils.error_handlers import (
    AppException,
    ValidationException,
    app_exception_handler,
    validation_exception_handler
)
from ..utils.logging_config import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Tags metadata
tags_metadata = [
    {
        "name": "problem-validation",
        "description": "Operations for submitting and retrieving problem validation results",
    },
    {
        "name": "health",
        "description": "API health checking endpoints",
    },
    {
        "name": "analytics",
        "description": "Analytics and insights for validated problems",
    }
]

app = FastAPI(
    title="AI-Driven Problem Validation System",
    description="""
    An API for validating business problems and ideas using AI-driven analysis of social media discussions.
    
    Key features:
    - Problem statement validation
    - Sentiment analysis
    - Social media data collection
    - Real-time processing
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=tags_metadata,
    contact={
        "name": "Development Team",
        "email": "dev@example.com",
    },
    license_info={
        "name": "Private",
    }
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "token",
                    "scopes": {}
                }
            }
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Add monitoring middleware
app.add_middleware(MonitoringMiddleware)

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

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting up API service")
    message_queue.connect()
    message_queue.declare_queue("validation_tasks")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down API service")
    message_queue.disconnect()

# Health check endpoint
@app.get("/health", 
    tags=["health"],
    summary="Check API health status",
    description="Get detailed health status of the API and its dependencies",
    response_description="Detailed health check response",
    responses={
        200: {
            "description": "System is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "timestamp": "2025-05-10T12:00:00Z",
                        "version": "1.0.0",
                        "services": {
                            "redis": "connected",
                            "mongodb": "connected",
                            "rabbitmq": "connected"
                        },
                        "system": {
                            "cpu_usage": "23.5%",
                            "memory_usage": "45.2%",
                            "uptime": "2d 3h 45m"
                        }
                    }
                }
            }
        },
        503: {
            "description": "System is unhealthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "unhealthy",
                        "timestamp": "2025-05-10T12:00:00Z",
                        "errors": [
                            {"service": "redis", "status": "disconnected"},
                            {"service": "mongodb", "status": "error", "details": "Connection timeout"}
                        ]
                    }
                }
            }
        }
    }
)
async def health_check():
    """Check the health of all system components."""
    import psutil
    
    try:
        # Check service connections
        service_status = {
            "redis": "connected" if cache_service.is_connected() else "disconnected",
            "mongodb": "connected" if storage_service.is_connected() else "disconnected",
            "rabbitmq": "connected" if message_queue.is_connected() else "disconnected"
        }

        # Check system resources
        system_status = {
            "cpu_usage": f"{psutil.cpu_percent()}%",
            "memory_usage": f"{psutil.virtual_memory().percent}%",
            "uptime": time.strftime("%Hh %Mm %Ss", time.gmtime(time.time() - psutil.boot_time()))
        }

        # Check for any unhealthy services
        errors = [
            {"service": service, "status": status}
            for service, status in service_status.items()
            if status != "connected"
        ]

        response = {
            "status": "healthy" if not errors else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": app.version,
            "services": service_status,
            "system": system_status
        }

        if errors:
            response["errors"] = errors
            return JSONResponse(status_code=503, content=response)

        return response
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "errors": [{"service": "health_check", "status": "error", "details": str(e)}]
            }
        )

@app.get("/metrics",
    tags=["health"],
    summary="Get system metrics",
    description="Get Prometheus metrics for system monitoring",
    response_description="Prometheus metrics in text format",
    responses={
        200: {
            "description": "Metrics retrieved successfully",
            "content": {
                "text/plain": {
                    "example": """
                    # HELP http_requests_total Total number of HTTP requests
                    # TYPE http_requests_total counter
                    http_requests_total{method="GET",endpoint="/health",status="200"} 45
                    """
                }
            }
        }
    }
)
async def metrics():
    """Get Prometheus metrics."""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from fastapi.responses import Response
    
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

@app.post("/validate", 
    tags=["problem-validation"],
    summary="Submit a problem statement for validation",
    response_model=ValidationRequest,
    responses={
        201: {
            "description": "Validation request created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "request_id": "550e8400-e29b-41d4-a716-446655440000",
                        "status": "processing",
                        "created_at": "2025-05-10T12:00:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Invalid input",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid problem statement format"}
                }
            }
        },
        401: {
            "description": "Authentication required"
        }
    }
)
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
        
        # Store request in memory
        active_validations[problem_id] = validation_request
        
        # Queue validation task
        success = message_queue.publish(
            "validation_tasks",
            {
                "problem_id": problem_id,
                "problem": problem.dict()
            }
        )
        
        if not success:
            # Clean up and raise error if queueing fails
            del active_validations[problem_id]
            raise ValidationException("Failed to queue validation task. Please try again.")
        
        # Update status to processing after successful queueing
        validation_request.status = "processing"
        return validation_request
    
    except ValidationException as e:
        raise
    except Exception as e:
        logger.error(f"Error creating validation request: {str(e)}")
        raise ValidationException("An error occurred while processing your request.")

@app.get("/validate/{problem_id}", 
    tags=["problem-validation"],
    summary="Get validation status",
    response_model=ValidationRequest,
    responses={
        200: {
            "description": "Validation status retrieved successfully"
        },
        404: {
            "description": "Validation request not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Validation request not found for the given ID"}
                }
            }
        },
        401: {
            "description": "Authentication required"
        }
    }
)
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

@app.get("/results/{problem_id}",
    tags=["problem-validation"],
    summary="Get validation results",
    response_model=ValidationResult,
    responses={
        200: {
            "description": "Validation results retrieved successfully"
        },
        404: {
            "description": "Results not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Validation results not found for the given ID"}
                }
            }
        },
        401: {
            "description": "Authentication required"
        }
    }
)
async def get_validation_results(
    problem_id: str,
    current_user: User = Depends(rate_limited_user)
) -> ValidationResult:
    """Get validation results for a problem."""
    validation_request = active_validations.get(problem_id)
    if not validation_request:
        # Try to load from storage
        stored_result = storage_service.get_validation_result(problem_id)
        if stored_result:
            return ValidationResult(**stored_result)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Validation results not found for the given ID"
        )
    if validation_request.result:
        return validation_request.result
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Validation results not found for the given ID"
    )

@app.get("/analytics/trends",
    tags=["analytics"],
    summary="Get validation trends and insights",
    responses={
        200: {
            "description": "Analytics data retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "total_validations": 150,
                        "average_sentiment": 0.65,
                        "popular_keywords": ["fintech", "AI", "sustainability"],
                        "industry_distribution": {
                            "Fintech": 30,
                            "Healthcare": 25,
                            "Education": 20
                        }
                    }
                }
            }
        },
        401: {
            "description": "Authentication required"
        }
    }
)
async def get_trends(current_user: User = Depends(rate_limited_user)):
    """Get validation trends and insights."""
    try:
        analytics_data = storage_service.get_analytics_data()
        return analytics_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/problems", 
    tags=["problem-validation"],
    summary="List all validated problems",
    response_model=List[ValidationResult],
    responses={
        200: {
            "description": "Validated problems retrieved successfully"
        },
        401: {
            "description": "Authentication required"
        }
    }
)
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

@app.delete("/problems/{problem_id}", 
    tags=["problem-validation"],
    summary="Delete a validated problem",
    responses={
        200: {
            "description": "Problem deleted successfully"
        },
        401: {
            "description": "Authentication required"
        },
        500: {
            "description": "Internal server error"
        }
    }
)
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
