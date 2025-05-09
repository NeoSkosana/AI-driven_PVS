"""
Redis cache service for the Problem Validation System.
"""
from typing import Any, Optional
import json
import redis
import os
from datetime import timedelta
from dotenv import load_dotenv

class RedisCache:
    """Redis cache implementation."""
    
    def __init__(self):
        """Initialize Redis connection."""
        load_dotenv()
        
        self.redis = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            decode_responses=True
        )
        
    def set(self, key: str, value: Any, expire_in: int = 3600) -> bool:
        """
        Set a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            expire_in: Time in seconds until the key expires
            
        Returns:
            bool: True if successful
        """
        try:
            serialized = json.dumps(value)
            return self.redis.setex(key, timedelta(seconds=expire_in), serialized)
        except Exception as e:
            print(f"Cache set error: {str(e)}")
            return False
            
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        try:
            data = self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            print(f"Cache get error: {str(e)}")
            return None
            
    def delete(self, key: str) -> bool:
        """
        Delete a key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            bool: True if successful
        """
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            print(f"Cache delete error: {str(e)}")
            return False
            
    def clear(self) -> bool:
        """
        Clear all cached data.
        
        Returns:
            bool: True if successful
        """
        try:
            return bool(self.redis.flushdb())
        except Exception as e:
            print(f"Cache clear error: {str(e)}")
            return False
