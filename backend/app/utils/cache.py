import json
from typing import Optional, Any
from functools import wraps
import redis
from app.core.config import settings

# Initialize Redis client
redis_client = None
if settings.REDIS_URL:
    try:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    except Exception:
        redis_client = None


def get_cache(key: str) -> Optional[Any]:
    """Get value from cache"""
    if not redis_client:
        return None
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception:
        return None


def set_cache(key: str, value: Any, expiry: int = 300) -> None:
    """Set value in cache with expiry in seconds (default 5 minutes)"""
    if not redis_client:
        return
    try:
        redis_client.setex(key, expiry, json.dumps(value))
    except Exception:
        pass


def delete_cache(pattern: str) -> None:
    """Delete cache keys matching pattern"""
    if not redis_client:
        return
    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
    except Exception:
        pass


def cache_response(key_prefix: str, expiry: int = 300):
    """Decorator to cache function responses"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key from function arguments
            cache_key = f"{key_prefix}:{str(args)}:{str(kwargs)}"

            # Try to get from cache
            cached_value = get_cache(cache_key)
            if cached_value is not None:
                return cached_value

            # Call function and cache result
            result = await func(*args, **kwargs)
            set_cache(cache_key, result, expiry)
            return result
        return wrapper
    return decorator
