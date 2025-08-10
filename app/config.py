"""
Configuration management for Project Thalassa.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application settings
    app_name: str = "Project Thalassa"
    app_version: str = "0.1.0"
    debug: bool = False

    # Security settings
    bearer_token: str | None = None

    # File storage settings (configurable via environment)
    upload_dir: str = "uploads"
    results_dir: str = "results"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: set[str] = {".fastq", ".fq", ".fastq.gz", ".fq.gz"}

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
