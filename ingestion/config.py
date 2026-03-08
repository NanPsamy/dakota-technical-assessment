import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration management for the ingestion service"""

        # Ingestion settings
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", "5"))  # seconds
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))  # seconds

    def __init__(self):
        self.eia_api_key = os.getenv('EIA_API_KEY', 'bgYUdcNb4ZabkgPgMVFB0tbbahaf80nZygceUoYk')
        self.eia_base_url = os.getenv('EIA_BASE_URL', 'https://api.eia.gov/v2/petroleum/pri/gnd/')
        self.api_base_url = os.getenv('API_BASE_URL', 'http://localhost:8000')

        if not self.eia_api_key:
            raise ValueError("EIA_API_KEY environment variable is required")

    @property
    def db_config(self) -> Dict[str, Any]:
        """Database configuration"""
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'database': os.getenv('DB_NAME', 'energy_analytics'),
            'user': os.getenv('DB_USER', 'energy_user'),
            'password': os.getenv('DB_PASSWORD', 'energy_password')
        }

    @property
    def eia_api_key(self) -> str:
        return self._eia_api_key

    @eia_api_key.setter
    def eia_api_key(self, value: str):
        self._eia_api_key = value

    @property
    def api_base_url(self) -> str:
        return self._api_base_url

    @api_base_url.setter
    def api_base_url(self, value: str):
        self._api_base_url = value

# Global config instance
config = Config()