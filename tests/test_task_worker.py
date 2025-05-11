"""Tests for the validation task worker."""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.queue.task_worker import TaskWorker

@pytest.fixture
def mock_services():
    """Create mock services for testing."""
    with patch('src.queue.task_worker.MessageQueue') as mock_mq, \
         patch('src.queue.task_worker.RedditCollector') as mock_rc, \
         patch('src.queue.task_worker.SentimentAnalyzer') as mock_sa, \
         patch('src.queue.task_worker.StorageService') as mock_ss:
        yield {
            'message_queue': mock_mq.return_value,
            'reddit_collector': mock_rc.return_value,
            'sentiment_analyzer': mock_sa.return_value,
            'storage_service': mock_ss.return_value
        }

@pytest.fixture
def worker(mock_services):
    """Create a TaskWorker instance with mock services."""
    return TaskWorker()

def test_worker_initialization(worker, mock_services):
    """Test worker initialization."""
    assert worker.message_queue == mock_services['message_queue']
    assert worker.reddit_collector == mock_services['reddit_collector']
    assert worker.sentiment_analyzer == mock_services['sentiment_analyzer']
    assert worker.storage_service == mock_services['storage_service']
    assert not worker.should_stop

def test_process_task_success(worker, mock_services):
    """Test successful task processing."""
    # Setup mock data
    posts = [{"id": "test1", "content": "test content"}]
    analysis_result = {
        "sentiment_summary": {"overall_sentiment": "POSITIVE"},
        "engagement_metrics": {"total_engagement": 100},
        "temporal_analysis": {"avg_posts_per_day": 5},
        "validation_score": 0.85,
        "confidence_score": 0.9,
        "validation_flags": []
    }
    
    # Configure mocks
    mock_services['reddit_collector'].collect_posts.return_value = posts
    mock_services['sentiment_analyzer'].analyze_problem_validation.return_value = analysis_result
    
    # Process task
    task_message = {
        "problem_id": "test123",
        "problem": {
            "keywords": ["test"]
        }
    }
    worker.process_task(task_message)
    
    # Verify processing
    mock_services['reddit_collector'].collect_posts.assert_called_once()
    mock_services['sentiment_analyzer'].analyze_problem_validation.assert_called_once_with(posts)
    mock_services['storage_service'].store_validation_result.assert_called_once()
    
    # Verify stored result
    stored_result = mock_services['storage_service'].store_validation_result.call_args[0][1]
    assert stored_result["problem_id"] == "test123"
    assert stored_result["sentiment_summary"] == analysis_result["sentiment_summary"]
    assert stored_result["validation_score"] == analysis_result["validation_score"]

def test_process_task_invalid_message(worker, mock_services):
    """Test processing with invalid message format."""
    worker.process_task({})  # Empty message
    mock_services['storage_service'].store_validation_result.assert_not_called()

def test_process_task_error(worker, mock_services):
    """Test error handling during task processing."""
    # Setup mock to raise error
    mock_services['reddit_collector'].collect_posts.side_effect = Exception("Test error")
    
    # Process task
    task_message = {
        "problem_id": "test123",
        "problem": {
            "keywords": ["test"]
        }
    }
    worker.process_task(task_message)
    
    # Verify error result was stored
    mock_services['storage_service'].store_validation_result.assert_called_once()
    stored_result = mock_services['storage_service'].store_validation_result.call_args[0][1]
    assert stored_result["problem_id"] == "test123"
    assert stored_result["status"] == "failed"
    assert "Test error" in stored_result["error"]

def test_process_task_with_retry_success_after_failure(worker, mock_services):
    """Test retry logic with eventual success."""
    # Setup mock to fail twice then succeed
    fail_count = [0]
    def collect_posts_with_failures(*args, **kwargs):
        fail_count[0] += 1
        if fail_count[0] <= 2:  # Fail first two attempts
            raise Exception("Temporary failure")
        return [{"id": "test1", "content": "test content"}]
    
    mock_services['reddit_collector'].collect_posts.side_effect = collect_posts_with_failures
    
    # Process task
    task_message = {
        "problem_id": "test123",
        "problem": {
            "keywords": ["test"]
        }
    }
    worker.process_task_with_retry(task_message, max_retries=3, retry_delay=0)
    
    # Verify processing and storage
    assert mock_services['reddit_collector'].collect_posts.call_count == 3
    assert mock_services['sentiment_analyzer'].analyze_problem_validation.call_count == 1
    assert mock_services['storage_service'].store_validation_result.call_count == 1

def test_process_task_with_retry_all_attempts_fail(worker, mock_services):
    """Test retry logic when all attempts fail."""
    # Setup mock to always fail
    mock_services['reddit_collector'].collect_posts.side_effect = Exception("Persistent failure")
    
    # Process task
    task_message = {
        "problem_id": "test123",
        "problem": {
            "keywords": ["test"]
        }
    }
    worker.process_task_with_retry(task_message, max_retries=3, retry_delay=0)
    
    # Verify processing and error storage
    assert mock_services['reddit_collector'].collect_posts.call_count == 3
    mock_services['storage_service'].store_validation_result.assert_called_once()
    error_result = mock_services['storage_service'].store_validation_result.call_args[0][1]
    assert error_result["status"] == "failed"
    assert "Persistent failure" in error_result["error"]
