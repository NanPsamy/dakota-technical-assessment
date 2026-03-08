import logging
from datetime import date
from typing import Set
from config import config
from eia_client import EIAClient
from fastapi_client import FastAPIClient
from database_writer import DatabaseWriter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataIngestion:
    """Main data ingestion orchestrator"""

    def __init__(self):
        self.eia_client = EIAClient(config.eia_api_key)
        self.api_client = FastAPIClient(config.api_base_url)
        self.db_writer = DatabaseWriter(config.db_config)

    def run_ingestion(self) -> None:
        """Run the complete ingestion process"""
        logger.info("Starting data ingestion process")

        try:
            # Fetch and store EIA data
            eia_records = self.eia_client.fetch_data()
            self.db_writer.store_eia_data(eia_records)

            # Extract unique area codes from EIA data
            area_codes: Set[str] = set(r['area_code'] for r in eia_records if r['area_code'])

            # Fetch and store enrichment data for each area
            for area_code in area_codes:
                try:
                    enrichment_data = self.api_client.fetch_enrichment(area_code)
                    self.db_writer.store_enrichment_data(enrichment_data)
                except Exception as e:
                    logger.error(f"Failed to fetch enrichment for {area_code}: {e}")
                    continue

            logger.info("Data ingestion completed successfully")

        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            raise

if __name__ == "__main__":
    ingestion = DataIngestion()
    ingestion.run_ingestion()