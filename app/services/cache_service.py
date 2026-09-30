"""
Redis-based caching service for tagging results
"""
import redis
import json
from typing import Optional
from ..config import settings


class CacheService:
    """
    Redis cache for storing tagging results and frequently accessed data.
    Reduces redundant computation and improves API latency.
    """

    def __init__(self, redis_url: str = None):
        """
        Initialize cache service
        
        Args:
            redis_url: Redis connection URL (uses config default if None)
        """
        self.redis_url = redis_url or settings.REDIS_URL
        
        try:
            self.client = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self.client.ping()
            self.connected = True
        except Exception as e:
            print(f"Warning: Could not connect to Redis: {e}")
            self.connected = False
            self.client = None

    def is_connected(self) -> bool:
        """Check if Redis connection is active"""
        if not self.connected or self.client is None:
            return False
        
        try:
            self.client.ping()
            return True
        except Exception:
            return False

    def get(self, key: str) -> Optional[str]:
        """
        Get value from cache
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found/not connected
        """
        if not self.client:
            return None
        
        try:
            return self.client.get(key)
        except Exception as e:
            print(f"Cache get error: {e}")
            return None

    def set(self, key: str, value: str, ttl: int = None) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
        
        Returns:
            True if successful
        """
        if not self.client:
            return False
        
        try:
            if ttl:
                self.client.setex(key, ttl, value)
            else:
                self.client.set(key, value)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete value from cache
        
        Args:
            key: Cache key
        
        Returns:
            True if successful
        """
        if not self.client:
            return False
        
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern
        
        Args:
            pattern: Pattern to match (e.g., "tagging:*")
        
        Returns:
            Number of keys deleted
        """
        if not self.client:
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache clear error: {e}")
            return 0

    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.client:
            return {"connected": False}
        
        try:
            info = self.client.info()
            return {
                "connected": True,
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_commands_processed": info.get("total_commands_processed")
            }
        except Exception as e:
            return {"connected": False, "error": str(e)}
