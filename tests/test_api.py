import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from src.main import create_app

def test_validate_problem(test_client, mock_reddit_collector, mock_sentiment_analyzer, mock_storage_service):
    """Test problem validation endpoint."""
    response = test_client.post("/api/v1/validate", json={
        "title": "Test Problem",
        "description": "This is a test problem statement",
        "keywords": ["test", "problem"],
        "target_market": "developers"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert data["status"] == "processing"

def test_get_validation_status(test_client):
    """Test getting validation status."""
    # First create a validation request
    response = test_client.post("/api/v1/validate", json={
        "title": "Test Problem",
        "description": "This is a test problem statement",
        "keywords": ["test", "problem"]
    })
    
    problem_id = response.json()["request_id"]
    
    # Get its status
    response = test_client.get(f"/api/v1/validate/{problem_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["request_id"] == problem_id

def test_get_nonexistent_validation(test_client):
    """Test getting status of nonexistent validation."""
    response = test_client.get("/api/v1/validate/nonexistent")
    assert response.status_code == 404

def test_list_problems(test_client, mock_storage_service):
    """Test listing all problems."""
    # Store some test data first
    test_data = {
        "problem_id": "test123",
        "timestamp": datetime.utcnow(),
        "sentiment_summary": {},
        "engagement_metrics": {},
        "temporal_analysis": {},
        "validation_score": 0.85,
        "relevant_posts": []
    }
    mock_storage_service.store_collected_data(test_data, "test123")
    
    response = test_client.get("/api/v1/problems")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_delete_problem(test_client, mock_storage_service):
    """Test deleting a problem."""
    # Store test data first
    test_data = {"test": "data"}
    mock_storage_service.store_collected_data(test_data, "test123")
    
    response = test_client.delete("/api/v1/problems/test123")
    assert response.status_code == 200
    
    # Verify deletion
    response = test_client.get("/api/v1/problems/test123")
    assert response.status_code == 404
