import uuid
from typing import List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from datetime import datetime

from .models import ProblemStatement, ValidationResult, ValidationRequest
from ..data_collection.reddit_collector import RedditCollector
from ..analyzer.sentiment_analyzer import SentimentAnalyzer
from ..storage_service.mongodb_storage import StorageService

app = FastAPI(
    title="Problem Validation API",
    description="API for validating micro-SaaS business problems using Reddit data analysis",
    version="1.0.0"
)

# Initialize services
reddit_collector = RedditCollector()
sentiment_analyzer = SentimentAnalyzer()
storage_service = StorageService()

# Store background tasks
active_validations = {}

async def validate_problem_background(
    problem_id: str,
    problem: ProblemStatement
) -> None:
    """
    Background task to validate a problem statement.
    """
    try:
        # Find relevant subreddits
        subreddits = reddit_collector.find_relevant_subreddits(
            keywords=problem.keywords
        )
        
        # Collect posts from each subreddit
        all_posts = []
        for subreddit in subreddits:
            posts = reddit_collector.collect_posts(
                subreddit_name=subreddit,
                keywords=problem.keywords,
                time_filter='month',
                limit=100
            )
            all_posts.extend(posts)
            
        # Analyze collected data
        analysis_results = sentiment_analyzer.analyze_problem_validation(all_posts)
        
        # Store results
        validation_result = ValidationResult(
            problem_id=problem_id,
            timestamp=datetime.utcnow(),
            sentiment_summary=analysis_results["sentiment_summary"],
            engagement_metrics=analysis_results["engagement_metrics"],
            temporal_analysis=analysis_results["temporal_analysis"],
            validation_score=analysis_results["validation_score"],
            relevant_posts=all_posts
        )
        
        # Update storage
        storage_service.store_collected_data(
            validation_result.dict(),
            problem_id
        )
        
        # Update task status
        active_validations[problem_id].status = "completed"
        active_validations[problem_id].completed_at = datetime.utcnow()
        active_validations[problem_id].result = validation_result
        
    except Exception as e:
        active_validations[problem_id].status = "failed"
        active_validations[problem_id].completed_at = datetime.utcnow()
        print(f"Validation failed for problem {problem_id}: {str(e)}")

@app.post("/validate", response_model=ValidationRequest)
async def validate_problem(
    problem: ProblemStatement,
    background_tasks: BackgroundTasks
) -> ValidationRequest:
    """
    Submit a problem statement for validation.
    """
    problem_id = str(uuid.uuid4())
    
    # Create validation request
    validation_request = ValidationRequest(
        request_id=problem_id,
        status="processing",
        created_at=datetime.utcnow()
    )
    
    # Store request
    active_validations[problem_id] = validation_request
    
    # Start background validation
    background_tasks.add_task(
        validate_problem_background,
        problem_id,
        problem
    )
    
    return validation_request

@app.get("/validate/{problem_id}", response_model=ValidationRequest)
async def get_validation_status(problem_id: str) -> ValidationRequest:
    """
    Get the status of a problem validation request.
    """
    if problem_id not in active_validations:
        raise HTTPException(
            status_code=404,
            detail="Validation request not found"
        )
    
    return active_validations[problem_id]

@app.get("/problems", response_model=List[ValidationResult])
async def list_problems(limit: int = 100) -> List[ValidationResult]:
    """
    List all validated problems.
    """
    problems = storage_service.list_problems(limit=limit)
    return [
        ValidationResult(**problem["data"])
        for problem in problems
    ]

@app.delete("/problems/{problem_id}")
async def delete_problem(problem_id: str) -> dict:
    """
    Delete a validated problem and its results.
    """
    if not storage_service.delete_problem_data(problem_id):
        raise HTTPException(
            status_code=404,
            detail="Problem not found"
        )
    
    # Also remove from active validations if present
    active_validations.pop(problem_id, None)
    
    return {"status": "success", "message": "Problem deleted"}
