from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    SECRET_KEY: str
    DOMAIN: str = "http://localhost:8000"
    APP_NAME: str = "URL Shortener"

    DATABASE_URL: Optional[str] = None
    
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "url-shortener-dev"
    DB_USERNAME: str = "url-shortener-dev"
    DB_PASSWORD: str = "url-shortener-pass"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_CACHE_TTL: int = 3600
    REDIS_URL: Optional[str] = None

    # JWT
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def JWT_SECRET_KEY(self) -> str:
        return self.SECRET_KEY

    @property
    def effective_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def effective_redis_url(self) -> str:
        if self.REDIS_URL:
            return self.REDIS_URL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()