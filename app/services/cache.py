"""
Cliente simple de caché basado en Redis.
"""
from typing import Optional
import json

import redis

from app.config import settings


class RedisCache:
    def __init__(self, url: Optional[str] = None, default_ttl_seconds: Optional[int] = None) -> None:
        self.url = url or settings.REDIS_URL
        self.ttl = default_ttl_seconds or settings.CACHE_TTL_SECONDS
        self.client = redis.Redis.from_url(self.url, decode_responses=True)

    def get_json(self, key: str):
        try:
            val = self.client.get(key)
            if val is None:
                return None
            return json.loads(val)
        except Exception:
            return None

    def set_json(self, key: str, value, ttl_seconds: Optional[int] = None):
        try:
            ttl = ttl_seconds or self.ttl
            self.client.setex(key, ttl, json.dumps(value, ensure_ascii=False))
        except Exception:
            # Fail silently for cache errors
            pass


