"""
Application settings loaded from environment variables.
All LLM endpoint config lives here — never hardcoded elsewhere.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Primary and fallback LLM server URLs
    primary_endpoint: str = "https://chat.aps.work"
    secondary_endpoint: str = "https://chat2.aps.work"

    # Model name sent to both servers (must exist on both)
    model_name: str = "llama3"

    # Request timeout in seconds before triggering failover
    request_timeout: int = 30

    # App metadata
    app_name: str = "APS Internal Assistant"
    debug: bool = False

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "protected_namespaces": ("settings_",),  # allow model_name field
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings — only reads .env once per process."""
    return Settings()
