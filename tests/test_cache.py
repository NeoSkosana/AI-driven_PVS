"""Tests for Redis cache implementation."""
import pytest
from unittest.mock import Mock, patch
from src.cache.redis_cache import RedisCache

@pytest.fixture
def mock_redis():
    """Create a mock Redis instance."""
    with patch('redis.Redis') as mock:
        yield mock

@pytest.fixture
def cache_service(mock_redis):
    """Create a RedisCache instance with mocked Redis."""
    return RedisCache()

def test_set_value(cache_service, mock_redis):
    """Test setting a value in cache."""
    mock_redis.return_value.setex.return_value = True
    
    result = cache_service.set("test_key", {"test": "data"})
    assert result is True
    
    # Verify Redis setex was called with correct args
    mock_redis.return_value.setex.assert_called_once()

def test_get_value(cache_service, mock_redis):
    """Test getting a value from cache."""
    mock_redis.return_value.get.return_value = '{"test": "data"}'
    
    result = cache_service.get("test_key")
    assert result == {"test": "data"}
    
    # Verify Redis get was called
    mock_redis.return_value.get.assert_called_once_with("test_key")

def test_get_nonexistent_value(cache_service, mock_redis):
    """Test getting a non-existent value."""
    mock_redis.return_value.get.return_value = None
    
    result = cache_service.get("nonexistent")
    assert result is None

def test_delete_value(cache_service, mock_redis):
    """Test deleting a value from cache."""
    mock_redis.return_value.delete.return_value = 1
    
    result = cache_service.delete("test_key")
    assert result is True
    
    # Verify Redis delete was called
    mock_redis.return_value.delete.assert_called_once_with("test_key")

def test_clear_cache(cache_service, mock_redis):
    """Test clearing all cached data."""
    mock_redis.return_value.flushdb.return_value = True
    
    result = cache_service.clear()
    assert result is True
    
    # Verify Redis flushdb was called
    mock_redis.return_value.flushdb.assert_called_once()
