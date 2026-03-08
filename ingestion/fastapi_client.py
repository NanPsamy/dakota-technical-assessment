import logging
from datetime import date
from typing import Dict, Any
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

class EnrichmentData(BaseModel):
    period: date
    area_code: str
    wti_crude_price_usd: float
    brent_crude_price_usd: float
    crude_spread: float
    refinery_utilization_rate: float
    refinery_outage_index: float
    gasoline_inventory_million_barrels: float
    supply_disruption_index: float
    regional_demand_index: float
    vehicle_miles_traveled_index: float
    avg_temperature_c: float
    heating_degree_days: float
    cooling_degree_days: float
    pipeline_utilization_rate: float
    shipping_cost_index: float
    energy_volatility_index: float
    speculative_pressure_index: float
    hurricane_risk_index: float
    geopolitical_risk_index: float

class FastAPIClient:
    """Client for interacting with FastAPI enrichment service"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.RequestException, requests.HTTPError))
    )
    def fetch_enrichment(self, area_code: str, period: date = None) -> Dict[str, Any]:
        """Fetch enrichment data from FastAPI service"""
        if not period:
            # Default to latest week
            import datetime
            today = date.today()
            period = today - datetime.timedelta(days=today.weekday())

        url = f"{self.base_url}/enrich/{area_code}"
        params = {'period': period.isoformat()}

        logger.info(f"Fetching enrichment data for {area_code} on {period}")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        try:
            # Validate with Pydantic
            EnrichmentData(**data)
            logger.info(f"Successfully fetched enrichment data for {area_code}")
            return data
        except ValidationError as e:
            logger.error(f"Invalid enrichment data: {e}")
            raise