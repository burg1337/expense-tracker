from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # SQLite database (no installation needed)
    DATABASE_URL: str = "sqlite:///./expense_tracker.db"
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REDIS_URL: Optional[str] = None  # Redis is optional - app works without it

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
