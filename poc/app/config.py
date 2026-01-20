"""
Configuration settings for the Support-Led Ordering System POC.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://poc_user:poc_password@localhost:5433/support_system"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Freshchat
    FRESHCHAT_APP_ID: Optional[str] = None
    FRESHCHAT_APP_KEY: Optional[str] = None
    FRESHCHAT_WEBHOOK_SECRET: str = "default_secret"
    FRESHCHAT_API_URL: str = "https://craftmyplate-932159069325046075-cefb1bc4cb2de9817685613.freshchat.com/v2"  # Account specific URL
    
    # Freshdesk (for ticket integration)
    FRESHDESK_DOMAIN: str = "test2288"  # Your Freshdesk subdomain
    FRESHDESK_API_KEY: Optional[str] = None
    
    # Application
    DEBUG: bool = True
    APP_NAME: str = "Support-Led Ordering System POC"
    
    # Channel routing thresholds (in INR)
    THRESHOLD_LOW: float = 5000.0
    THRESHOLD_HIGH: float = 25000.0
    
    # Friction score threshold
    FRICTION_THRESHOLD: float = 50.0
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Debug: Print the database URL being used (mask password for security)
import re
masked_url = re.sub(r':([^:@]+)@', r':****@', settings.DATABASE_URL)
print(f"📌 Using DATABASE_URL: {masked_url}")
