"""Application settings loaded from environment."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for Polyglot."""

    app_env: str = "development"
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000
    device: str = "cuda"

    llm_provider: str = "ollama"
    llm_model: str = "qwen2.5:7b-instruct"
    ollama_base_url: str = "http://ollama:11434"
    anthropic_api_key: str | None = None

    whisper_model: str = "small"
    min_audio_ms: int = 300
    max_audio_ms: int = 30000
    pause_threshold_ms: int = 700
    database_url: str = "sqlite:///data/polyglot.db"
    demo_mode: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
