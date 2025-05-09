import uuid
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from datetime import datetime

from .models import ProblemStatement, ValidationResult, ValidationRequest
from ..data_collection.reddit_collector import RedditCollector
from ..analyzer.sentiment_analyzer import SentimentAnalyzer
from ..storage_service.mongodb_storage import StorageService
from ..cache.redis_cache import RedisCache
from ..queue.message_queue import MessageQueue

app = FastAPI(
    title="Problem Validation API",
    description="API for validating micro-SaaS business problems using Reddit data analysis",
    version="1.0.0"
)

# Initialize services
reddit_collector = RedditCollector()
sentiment_analyzer = SentimentAnalyzer()
storage_service = StorageService()
cache_service = RedisCache()
message_queue = MessageQueue()

# Ensure message queue connection
message_queue.connect()
message_queue.declare_queue("validation_tasks")

# Store background tasks
active_validations = {}

def process_validation_task(message: dict):
    """
    Process a validation task from the message queue.
    """
    try:
        problem_id = message["problem_id"]
        problem = ProblemStatement(**message["problem"])
        
        # Check cache first
        cached_result = cache_service.get(f"validation:{problem_id}")
        if cached_result:
            print(f"Cache hit for problem {problem_id}")
            active_validations[problem_id].status = "completed"
            active_validations[problem_id].completed_at = datetime.utcnow()
            active_validations[problem_id].result = ValidationResult(**cached_result)
            return
            
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
        
        # Create validation result
        validation_result = ValidationResult(
            problem_id=problem_id,
            timestamp=datetime.utcnow(),
            sentiment_summary=analysis_results["sentiment_summary"],
            engagement_metrics=analysis_results["engagement_metrics"],
            temporal_analysis=analysis_results["temporal_analysis"],
            validation_score=analysis_results["validation_score"],
            relevant_posts=all_posts
        )
        
        # Store results
        storage_service.store_collected_data(
            validation_result.dict(),
            problem_id
        )
        
        # Cache results
        cache_service.set(
            f"validation:{problem_id}",
            validation_result.dict(),
            expire_in=3600  # Cache for 1 hour
        )
        
        # Update task status
        active_validations[problem_id].status = "completed"
        active_validations[problem_id].completed_at = datetime.utcnow()
        active_validations[problem_id].result = validation_result
        
    except Exception as e:
        print(f"Validation task failed: {str(e)}")
        if problem_id in active_validations:
            active_validations[problem_id].status = "failed"
            active_validations[problem_id].completed_at = datetime.utcnow()

# Start consuming validation tasks
message_queue.channel.basic_consume(
    queue="validation_tasks",
    on_message_callback=lambda ch, method, props, body: process_validation_task(body)
)

@app.post("/validate", response_model=ValidationRequest)
async def validate_problem(
    problem: ProblemStatement
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
    
    # Queue validation task
    message_queue.publish(
        "validation_tasks",
        {
            "problem_id": problem_id,
            "problem": problem.dict()
        }
    )
    
    return validation_request

@app.get("/validate/{problem_id}", response_model=ValidationRequest)
async def get_validation_status(problem_id: str) -> ValidationRequest:
    """
    Get the status of a problem validation request.
    """
    # Try cache first
    cached_result = cache_service.get(f"validation:{problem_id}")
    if cached_result:
        return ValidationRequest(
            request_id=problem_id,
            status="completed",
            created_at=datetime.fromisoformat(cached_result["timestamp"]),
            completed_at=datetime.utcnow(),
            result=ValidationResult(**cached_result)
        )
    
    # Check active validations
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
    # Try cache first
    cached_problems = cache_service.get("problems_list")
    if cached_problems:
        return [ValidationResult(**p) for p in cached_problems]
    
    # Get from storage
    problems = storage_service.list_problems(limit=limit)
    problem_list = [ValidationResult(**problem["data"]) for problem in problems]
    
    # Cache results
    cache_service.set("problems_list", [p.dict() for p in problem_list], expire_in=300)
    
    return problem_list

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
    
    # Remove from cache
    cache_service.delete(f"validation:{problem_id}")
    cache_service.delete("problems_list")  # Invalidate problems list cache
    
    # Remove from active validations if present
    active_validations.pop(problem_id, None)
    
    return {"status": "success", "message": "Problem deleted"}
