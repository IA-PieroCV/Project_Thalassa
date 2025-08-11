"""
Configuration management for Project Thalassa.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application settings
    app_name: str = "Project Thalassa"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # Security settings
    bearer_token: str | None = None
    secret_key: str = "your-secret-key-here"
    access_token_expire_minutes: int = 30

    # File storage settings (configurable via environment)
    upload_dir: str = "uploads"
    results_dir: str = "results"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    max_file_size_mb: int = 100  # For backward compatibility with .env
    allowed_extensions: set[str] = {".fastq", ".fq", ".fastq.gz", ".fq.gz"}

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    # Logging settings
    log_level: str = "INFO"
    log_file: str = "logs/thalassa.log"

    # CORS settings
    allowed_origins: str = "http://localhost:3000,http://localhost:8080"

    # Risk assessment thresholds
    critical_risk_threshold: float = 0.8
    high_risk_threshold: float = 0.6
    medium_risk_threshold: float = 0.4

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
