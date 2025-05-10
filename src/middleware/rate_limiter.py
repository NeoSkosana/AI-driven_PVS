"""Rate limiting middleware for the API."""
from fastapi import HTTPException, Request, status
from datetime import datetime, timedelta
from typing import Tuple, Optional
from ..cache.redis_cache import RedisCache

class RateLimiter:
    """Rate limiting implementation using Redis."""
    
    def __init__(self, redis_cache: RedisCache):
        self.cache = redis_cache
        # Default limits
        self.default_rate_limits = {
            "validate": (5, timedelta(minutes=15)),  # 5 requests per 15 minutes
            "list": (30, timedelta(minutes=15)),     # 30 requests per 15 minutes
            "status": (60, timedelta(minutes=15)),   # 60 requests per 15 minutes
        }
    
    def _get_cache_key(self, request: Request, user_id: str) -> str:
        """Generate a cache key for rate limiting."""
        path = request.url.path.strip("/")
        endpoint = path.split("/")[0]  # Get the base endpoint
        return f"rate_limit:{user_id}:{endpoint}"
    
    def _get_rate_limit(self, endpoint: str) -> Tuple[int, timedelta]:
        """Get rate limit configuration for an endpoint."""
        # Remove any path parameters for matching
        base_endpoint = endpoint.split("/")[0]
        return self.default_rate_limits.get(
            base_endpoint, 
            (100, timedelta(minutes=15))  # Default: 100 requests per 15 minutes
        )
    
    async def check_rate_limit(
        self, 
        request: Request, 
        user_id: str
    ) -> None:
        """
        Check if the request is within rate limits.
        
        Args:
            request: The incoming request
            user_id: The ID of the authenticated user
            
        Raises:
            HTTPException: If rate limit is exceeded
        """
        path = request.url.path.strip("/")
        requests_limit, time_window = self._get_rate_limit(path)
        cache_key = self._get_cache_key(request, user_id)
        
        # Get current request count
        current_count = self.cache.get(cache_key) or 0
        
        if current_count >= requests_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {time_window.total_seconds() / 60} minutes"
            )
        
        # Increment request count
        if current_count == 0:
            # First request, set expiry
            self.cache.setex(
                cache_key,
                int(time_window.total_seconds()),
                str(1)
            )
        else:
            # Increment existing count
            self.cache.incr(cache_key)
