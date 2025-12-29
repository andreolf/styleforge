"""Application configuration using pydantic-settings."""

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    
    # Storage Configuration
    upload_dir: Path = Path("./data/uploads")
    output_dir: Path = Path("./data/outputs")
    metadata_dir: Path = Path("./data/metadata")
    
    # File Upload Limits
    max_file_size_mb: int = 10
    allowed_extensions: str = "jpg,jpeg,png,webp"
    
    # Rate Limiting
    rate_limit_per_minute: int = 30
    
    # Image Generator: 'stub', 'huggingface', or 'real'
    image_generator: str = "huggingface"
    
    # AI API tokens (optional - free tier works without for HuggingFace)
    replicate_api_token: str = ""
    huggingface_api_token: str = ""
    
    # CORS Configuration
    cors_origins: str = "http://localhost:3000"
    
    # Logging
    log_level: str = "INFO"
    
    @property
    def max_file_size_bytes(self) -> int:
        """Maximum file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """List of allowed file extensions."""
        return [ext.strip().lower() for ext in self.allowed_extensions.split(",")]
    
    @property
    def cors_origins_list(self) -> List[str]:
        """List of allowed CORS origins."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    def ensure_directories(self) -> None:
        """Create storage directories if they don't exist."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    settings.ensure_directories()
    return settings

