"""
Configuration management for the Content Creation Engine.
Loads environment variables and provides a centralized settings object.
"""

from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
try:
    from pydantic_settings import BaseSettings
except ImportError:
    # For pydantic v1
    from pydantic import BaseSettings

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    anthropic_api_key: str
    firecrawl_api_key: Optional[str] = None

    # WordPress Configuration
    wordpress_site_url: Optional[str] = None
    wordpress_username: Optional[str] = None
    wordpress_app_password: Optional[str] = None

    # Application Settings
    app_name: str = "Content Creation Engine"
    debug: bool = False

    # Memory Storage
    memory_base_path: Path = Path("app/memory")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Create a singleton settings instance
settings = Settings()
