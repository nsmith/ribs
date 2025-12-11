"""Application settings using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # OpenAI Configuration
    openai_api_key: str

    # AWS S3 Vectors Configuration
    aws_region: str = "us-east-1"
    s3_vectors_bucket: str = "ribs-gift-recommendations"
    s3_vectors_index: str = "gifts"

    # Server Configuration
    mcp_server_name: str = "gift-recommendations"
    log_level: str = "INFO"

    # Recommendation Settings
    default_recommendation_limit: int = 5
    min_recommendation_limit: int = 3
    max_recommendation_limit: int = 10
    relevance_threshold: float = 0.5
    embedding_dimensions: int = 1536


def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
