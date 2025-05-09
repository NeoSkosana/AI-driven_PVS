import pytest
from datetime import datetime
import mongomock
from src.storage_service.mongodb_storage import StorageService

@pytest.fixture
def storage_service():
    """Create a StorageService with mongomock."""
    service = StorageService()
    service.client = mongomock.MongoClient()
    service.db = service.client["problem_validation"]
    return service

def test_store_collected_data(storage_service):
    """Test storing collected data."""
    data = {
        "sentiment_summary": {
            "overall_sentiment": "POSITIVE",
            "positive_ratio": 0.7
        },
        "validation_score": 0.85
    }
    
    problem_id = "test123"
    doc_id = storage_service.store_collected_data(data, problem_id)
    
    assert doc_id is not None
    stored_data = storage_service.get_problem_data(problem_id)
    assert stored_data is not None
    assert stored_data["data"] == data

def test_get_nonexistent_problem(storage_service):
    """Test getting a problem that doesn't exist."""
    result = storage_service.get_problem_data("nonexistent")
    assert result is None

def test_update_analysis_results(storage_service):
    """Test updating analysis results."""
    # First store some data
    problem_id = "test123"
    initial_data = {"validation_score": 0.5}
    storage_service.store_collected_data(initial_data, problem_id)
    
    # Update the analysis
    new_results = {"validation_score": 0.8}
    success = storage_service.update_analysis_results(problem_id, new_results)
    
    assert success
    updated_data = storage_service.get_problem_data(problem_id)
    assert updated_data["data"]["analysis_results"] == new_results

def test_list_problems(storage_service):
    """Test listing all problems."""
    # Store some test data
    for i in range(3):
        storage_service.store_collected_data(
            {"test": f"data{i}"},
            f"problem{i}"
        )
    
    problems = storage_service.list_problems(limit=2)
    assert len(problems) == 2

def test_delete_problem(storage_service):
    """Test deleting a problem."""
    # Store test data
    problem_id = "test123"
    storage_service.store_collected_data({"test": "data"}, problem_id)
    
    # Delete it
    success = storage_service.delete_problem_data(problem_id)
    assert success
    
    # Verify it's gone
    assert storage_service.get_problem_data(problem_id) is None
