import redis.asyncio as redis
from typing import Optional, Any
import json
from .config import settings
import logging

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self.client: Optional[redis.Redis] = None
    
    async def connect(self):
        if not settings.REDIS_URL and settings.REDIS_HOST == "localhost":
            return
            
        try:
            self.client = await redis.from_url(
                settings.effective_redis_url,
                decode_responses=True
            )
            await self.client.ping()
        except Exception as e:
            self.client = None
    
    async def close(self):
        if self.client:
            await self.client.close()
            logger.info("Redis disconnected")
        
    async def get(self, key: str) -> Optional[str]:
        if not self.client:
            return None
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    async def set(self, key: str, value: str, ex: Optional[int] = None):
        if not self.client:
            return None
        try:
            await self.client.set(key, value, ex=ex)
        except Exception as e:
            logger.error(f"Redis set error: {e}")
    
    async def setex(self, key: str, seconds: int, value: str):
        await self.set(key, value, ex=seconds)
    
    async def delete(self, *keys: str) -> int:
        if not self.client:
            return 0
        try:
            return await self.client.delete(*keys)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        if not self.client:
            return False
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False
    
    async def expire(self, key: str, seconds: int) -> bool:
        if not self.client:
            return False
        try:
            return await self.client.expire(key, seconds)
        except Exception as e:
            logger.error(f"Redis expire error: {e}")
            return False
        
    async def incr(self, key: str) -> Optional[int]:
        if not self.client:
            return None
        try:
            return await self.client.incr(key)
        except Exception as e:
            logger.error(f"Redis incr error: {e}")
            return None
    
    async def decr(self, key: str) -> Optional[int]:
        if not self.client:
            return None
        try:
            return await self.client.decr(key)
        except Exception as e:
            logger.error(f"Redis decr error: {e}")
            return None
        
    async def set_json(self, key: str, data: Any, ex: Optional[int] = None):
        if not self.client:
            return None
        try:
            json_str = json.dumps(data)
            await self.set(key, json_str, ex=ex)
        except Exception as e:
            logger.error(f"Redis set_json error: {e}")
    
    async def get_json(self, key: str) -> Optional[Any]:
        if not self.client:
            return None
        try:
            data = await self.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Redis get_json error: {e}")
            return None
        
    async def cache_url(self, short_url: str, full_url: str):
        if not self.client:
            return
        await self.client.setex(
            f"url:{short_url}",
            settings.REDIS_CACHE_TTL,
            full_url
        )
    
    async def get_cached_url(self, short_url: str) -> Optional[str]:
        if not self.client:
            return None
        return await self.client.get(f"url:{short_url}")
    
    async def invalidate_url(self, short_url: str):
        if not self.client:
            return
        await self.client.delete(f"url:{short_url}")
    
    async def incr(self, key: str):
        if not self.client:
            return
        await self.client.incr(key)
    
    async def expire(self, key: str, seconds: int):
        if not self.client:
            return
        await self.client.expire(key, seconds)
    
    async def get(self, key: str) -> Optional[str]:
        if not self.client:
            return None
        return await self.client.get(key)
    
    async def close(self):
        if self.client:
            await self.client.close()

redis_client = RedisClient()