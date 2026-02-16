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
        """Buat koneksi ke Redis"""
        try:
            self.client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,  # Auto-decode bytes ke string
                health_check_interval=30  # Cek koneksi tiap 30 detik
            )
            # Test koneksi
            await self.client.ping()
            logger.info("Redis connected")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            # Fallback: tanpa Redis (app tetap jalan, tapi lambat)
            self.client = None
    
    async def close(self):
        """Tutup koneksi Redis"""
        if self.client:
            await self.client.close()
            logger.info("🔌 Redis disconnected")
    
    # ===== BASIC OPERATIONS =====
    
    async def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        if not self.client:
            return None
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    async def set(self, key: str, value: str, ex: Optional[int] = None):
        """Set key with optional expiry"""
        if not self.client:
            return None
        try:
            await self.client.set(key, value, ex=ex)
        except Exception as e:
            logger.error(f"Redis set error: {e}")
    
    async def setex(self, key: str, seconds: int, value: str):
        """Set with expiry (alias untuk set dengan ex)"""
        await self.set(key, value, ex=seconds)
    
    async def delete(self, *keys: str) -> int:
        """Delete one or more keys"""
        if not self.client:
            return 0
        try:
            return await self.client.delete(*keys)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.client:
            return False
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiry on existing key"""
        if not self.client:
            return False
        try:
            return await self.client.expire(key, seconds)
        except Exception as e:
            logger.error(f"Redis expire error: {e}")
            return False
    
    # ===== COUNTER OPERATIONS =====
    
    async def incr(self, key: str) -> Optional[int]:
        """Increment counter"""
        if not self.client:
            return None
        try:
            return await self.client.incr(key)
        except Exception as e:
            logger.error(f"Redis incr error: {e}")
            return None
    
    async def decr(self, key: str) -> Optional[int]:
        """Decrement counter"""
        if not self.client:
            return None
        try:
            return await self.client.decr(key)
        except Exception as e:
            logger.error(f"Redis decr error: {e}")
            return None
    
    # ===== JSON OPERATIONS =====
    
    async def set_json(self, key: str, data: Any, ex: Optional[int] = None):
        """Store Python object as JSON"""
        if not self.client:
            return None
        try:
            json_str = json.dumps(data)
            await self.set(key, json_str, ex=ex)
        except Exception as e:
            logger.error(f"Redis set_json error: {e}")
    
    async def get_json(self, key: str) -> Optional[Any]:
        """Get and parse JSON data"""
        if not self.client:
            return None
        try:
            data = await self.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Redis get_json error: {e}")
            return None
    
    # ===== URL SHORTENER SPECIFIC =====
    
    async def cache_url(self, short_code: str, long_url: str):
        """Cache URL untuk redirect cepat"""
        await self.setex(
            f"url:{short_code}", 
            settings.REDIS_CACHE_TTL, 
            long_url
        )
    
    async def get_cached_url(self, short_code: str) -> Optional[str]:
        """Dapatkan URL dari cache"""
        return await self.get(f"url:{short_code}")
    
    async def invalidate_url(self, short_code: str):
        """Hapus URL dari cache (misal pas delete/update)"""
        await self.delete(f"url:{short_code}")
    
    async def increment_click(self, short_code: str):
        key = f"clicks:{short_code}"
        await self.incr(key)
        await self.expire(key, 86400)
    
    async def get_daily_clicks(self, short_code: str) -> int:
        """Dapatkan jumlah clicks hari ini dari Redis"""
        val = await self.get(f"clicks:{short_code}")
        return int(val) if val else 0

# Singleton instance
redis_client = RedisClient()