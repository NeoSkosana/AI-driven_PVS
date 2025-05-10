"""Tests for the rate limiter middleware."""
import pytest
from fastapi import HTTPException, Request, status
from unittest.mock import Mock, AsyncMock
from datetime import timedelta

from src.middleware.rate_limiter import RateLimiter
from src.cache.redis_cache import RedisCache

@pytest.fixture
def mock_redis_cache():
    """Create a mock Redis cache."""
    cache = Mock(spec=RedisCache)
    cache.get.return_value = None
    cache.setex.return_value = True
    cache.incr.return_value = 1
    return cache

@pytest.fixture
def rate_limiter(mock_redis_cache):
    """Create a RateLimiter instance with mock cache."""
    return RateLimiter(mock_redis_cache)

@pytest.fixture
def mock_request():
    """Create a mock request."""
    request = Mock(spec=Request)
    request.url.path = "/validate"
    return request

@pytest.mark.asyncio
async def test_rate_limit_first_request(rate_limiter, mock_request):
    """Test rate limiting for first request."""
    await rate_limiter.check_rate_limit(mock_request, "test_user")
    
    cache_key = rate_limiter._get_cache_key(mock_request, "test_user")
    rate_limiter.cache.setex.assert_called_once_with(
        cache_key,
        900,  # 15 minutes in seconds
        "1"
    )

@pytest.mark.asyncio
async def test_rate_limit_subsequent_request(rate_limiter, mock_request):
    """Test rate limiting for subsequent requests."""
    rate_limiter.cache.get.return_value = "2"
    
    await rate_limiter.check_rate_limit(mock_request, "test_user")
    
    cache_key = rate_limiter._get_cache_key(mock_request, "test_user")
    rate_limiter.cache.incr.assert_called_once_with(cache_key)

@pytest.mark.asyncio
async def test_rate_limit_exceeded(rate_limiter, mock_request):
    """Test rate limiting when limit is exceeded."""
    rate_limiter.cache.get.return_value = "5"  # Max limit for /validate endpoint
    
    with pytest.raises(HTTPException) as exc_info:
        await rate_limiter.check_rate_limit(mock_request, "test_user")
    
    assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert "Rate limit exceeded" in exc_info.value.detail

@pytest.mark.asyncio
async def test_rate_limit_different_endpoints(rate_limiter):
    """Test rate limiting for different endpoints."""
    # Test validate endpoint
    validate_request = Mock(spec=Request)
    validate_request.url.path = "/validate"
    
    # Test list endpoint
    list_request = Mock(spec=Request)
    list_request.url.path = "/problems"
    
    # Should have different limits
    validate_limit, _ = rate_limiter._get_rate_limit("validate")
    list_limit, _ = rate_limiter._get_rate_limit("problems")
    
    assert validate_limit == 5  # Validate endpoint limit
    assert list_limit == 30  # List endpoint limit
