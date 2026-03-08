import os
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv


def _load_environment() -> None:
    """Load .env from explicit locations so local runs are predictable."""
    root_dir = Path(__file__).resolve().parents[1]
    candidates = [
        root_dir / ".env",
        Path(__file__).resolve().parent / ".env",
    ]

    for env_file in candidates:
        if env_file.exists():
            load_dotenv(dotenv_path=env_file, override=False)
            break
    else:
        # Fall back to default dotenv behavior if no expected file is present.
        load_dotenv(override=False)


_load_environment()


class Config:
    """Configuration management for the ingestion service."""

    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", "5"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

    def __init__(self) -> None:
        self._eia_api_key = os.getenv("EIA_API_KEY", "").strip()
        self._eia_base_url = os.getenv("EIA_BASE_URL", "https://api.eia.gov/v2").strip()
        self._api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000").strip()

        if not self._eia_api_key:
            raise ValueError("EIA_API_KEY environment variable is required (set in .env or runtime env)")

    @property
    def db_config(self) -> Dict[str, Any]:
        """Database configuration."""
        return {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "database": os.getenv("DB_NAME", "energy_analytics"),
            "user": os.getenv("DB_USER", "energy_user"),
            "password": os.getenv("DB_PASSWORD", "energy_password"),
        }

    @property
    def eia_api_key(self) -> str:
        return self._eia_api_key

    @property
    def eia_base_url(self) -> str:
        return self._eia_base_url

    @property
    def api_base_url(self) -> str:
        return self._api_base_url


config = Config()