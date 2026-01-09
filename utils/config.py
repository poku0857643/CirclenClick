"""Configuration management for CircleNClick."""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # API Keys
    google_factcheck_api_key: Optional[str] = None
    claimbuster_api_key: Optional[str] = None
    factiverse_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    redis_enabled: bool = False

    # FastAPI Server
    api_host: str = "localhost"
    api_port: int = 8080
    api_reload: bool = True

    # Model Settings
    model_confidence_threshold: float = 0.7
    cache_ttl_hours: int = 24
    max_cache_size_mb: int = 500

    # Processing Settings
    local_only_mode: bool = False
    cloud_timeout_seconds: int = 15
    max_concurrent_requests: int = 5

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/circlenclick.log"

    # Development
    debug: bool = False
    testing: bool = False

    # Paths
    @property
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent

    @property
    def models_dir(self) -> Path:
        """Get the models directory."""
        return self.project_root / "model" / "weights"

    @property
    def cache_dir(self) -> Path:
        """Get the cache directory."""
        return self.project_root / "cache"

    @property
    def logs_dir(self) -> Path:
        """Get the logs directory."""
        return self.project_root / "logs"

    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def has_cloud_apis(self) -> bool:
        """Check if any cloud API keys are configured."""
        return any([
            self.google_factcheck_api_key,
            self.claimbuster_api_key,
            self.factiverse_api_key,
            self.openai_api_key,
            self.anthropic_api_key
        ])


# Global settings instance
settings = Settings()

# Ensure directories exist
settings.ensure_directories()
