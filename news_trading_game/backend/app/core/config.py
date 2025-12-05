from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./news_trading_game.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Market Engine
    auction_interval_minutes: int = 1  # Set to 1 minute for troubleshooting
    auction_randomization_seconds: int = 10  # Reduced randomization for testing
    price_update_interval_seconds: int = 10  # More frequent price updates
    
    # Game Settings
    initial_cash: float = 10000.0
    max_topics_per_category: int = 5
    initial_shares_per_topic: int = 1000000
    
    # API
    api_v1_str: str = "/api/v1"
    project_name: str = "News Trading Game MVP"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
