import logging
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

class EIAData(BaseModel):
    series_id: str
    period: date
    value: Optional[float] = None
    area_name: str = None
    area_code: Optional[str] = None
    product_name: str
    product_code: str = None
    process_name: str = None
    process_code: str = None
    unit: str
    frequency: str
    dataset: str = "petroleum/pri/gnd"

class EIAClient:
    """Client for interacting with EIA API"""

    def __init__(self, api_key: str):
        self.api_key = api_key

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.RequestException, requests.HTTPError))
    )
    def fetch_data(self, offset: int = 0, length: int = 5000) -> List[Dict[str, Any]]:
        """Fetch data from EIA API with retries"""
        url = "https://api.eia.gov/v2/petroleum/pri/gnd/data/"
        params = {
            'frequency': 'weekly',
            'data[0]': 'value',
            'sort[0][column]': 'period',
            'sort[0][direction]': 'desc',
            'offset': offset,
            'length': length,
            'api_key': self.api_key
        }

        logger.info(f"Fetching EIA data with offset {offset}, length {length}")
        response = requests.get(url, params=params, timeout=30)
        logger.info(response.raise_for_status())
        response.raise_for_status()

        data = response.json()
        records = []

        for item in data.get('response', {}).get('data', []):
            try:
                # convert and coerce types explicitly
                series_id = str(item.get('series', ''))
                period_val = datetime.strptime(item['period'], '%Y-%m-%d').date()
                value_val = float(item['value']) if item.get('value') not in (None, '') else None
                area_name = item.get('area-name')
                area_code = item.get('duoarea')
                if area_code is not None:
                    area_code = str(area_code)
                product_name = str(item.get('product-name', ''))
                product_code = item.get('product')
                if product_code is not None:
                    product_code = str(product_code)
                process_name = item.get('process-name')
                process_code = item.get('process')
                if process_code is not None:
                    process_code = str(process_code)
                unit = str(item.get('units', ''))
                frequency = str(item.get('frequency', ''))

                record = {
                    'series_id': series_id,
                    'period': period_val,
                    'value': value_val,
                    'area_name': area_name,
                    'area_code': area_code,
                    'product_name': product_name,
                    'product_code': product_code,
                    'process_name': process_name,
                    'process_code': process_code,
                    'unit': unit,
                    'frequency': frequency,
                    'dataset': 'petroleum/pri/gnd'
                }
                # Validate with Pydantic (does additional coercion)
                EIAData(**record)
                records.append(record)
            except (ValueError, ValidationError) as e:
                logger.warning(f"Skipping invalid EIA record: {e}")

        logger.info(f"Successfully fetched {len(records)} EIA records")
        return records