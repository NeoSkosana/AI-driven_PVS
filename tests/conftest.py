import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock
import mongomock
import os
from datetime import datetime

from src.main import create_app
from src.data_collection.reddit_collector import RedditCollector
from src.analyzer.sentiment_analyzer import SentimentAnalyzer
from src.storage_service.mongodb_storage import StorageService

@pytest.fixture
def test_app():
    """Create a test FastAPI application."""
    return create_app()

@pytest.fixture
def test_client(test_app):
    """Create a test client for the FastAPI application."""
    return TestClient(test_app)

@pytest.fixture
def mock_reddit_collector():
    """Create a mock RedditCollector."""
    collector = Mock(spec=RedditCollector)
    
    # Mock find_relevant_subreddits
    collector.find_relevant_subreddits.return_value = [
        "startups",
        "SaaS",
        "entrepreneurship"
    ]
    
    # Mock collect_posts
    collector.collect_posts.return_value = [
        {
            "id": "post1",
            "title": "Test Post 1",
            "content": "This is a test post content",
            "score": 100,
            "num_comments": 10,
            "created_utc": datetime.utcnow().isoformat(),
            "url": "https://reddit.com/r/test/post1",
            "subreddit": "test",
            "top_comments": [
                {
                    "id": "comment1",
                    "body": "Test comment 1",
                    "score": 50,
                    "created_utc": datetime.utcnow().isoformat()
                }
            ]
        }
    ]
    
    return collector

@pytest.fixture
def mock_sentiment_analyzer():
    """Create a mock SentimentAnalyzer."""
    analyzer = Mock(spec=SentimentAnalyzer)
    
    analyzer.analyze_problem_validation.return_value = {
        "sentiment_summary": {
            "overall_sentiment": "POSITIVE",
            "positive_ratio": 0.7,
            "negative_ratio": 0.1,
            "neutral_ratio": 0.2,
            "average_score": 0.8
        },
        "engagement_metrics": {
            "avg_score": 100.0,
            "avg_comments": 10.0,
            "total_engagement": 110.0
        },
        "temporal_analysis": {
            "earliest_post": datetime.utcnow().isoformat(),
            "latest_post": datetime.utcnow().isoformat(),
            "avg_posts_per_day": 5.0
        },
        "validation_score": 0.85
    }
    
    return analyzer

@pytest.fixture
def mock_storage_service():
    """Create a mock StorageService with mongomock."""
    os.environ["MONGODB_URI"] = "mongodb://localhost:27017"
    storage = StorageService()
    storage.client = mongomock.MongoClient()
    storage.db = storage.client["problem_validation"]
    return storage
