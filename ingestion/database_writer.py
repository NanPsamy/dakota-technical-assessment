import logging
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import execute_values

logger = logging.getLogger(__name__)

class DatabaseWriter:
    """Handles database operations for storing ingested data"""

    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config

    def store_eia_data(self, records: List[Dict[str, Any]]) -> None:
        """Store EIA data in database"""
        if not records:
            logger.info("No EIA records to store")
            return

        conn = None
        try:
            conn = psycopg2.connect(**self.db_config)
            with conn.cursor() as cursor:
                # Insert into raw.eia_prices
                values = [(
                    r['series_id'], r['period'], r['value'], r['area_name'],
                    r['area_code'], r['product_name'], r['product_code'],
                    r['process_name'], r['process_code'], r['unit'],
                    r['frequency'], r['dataset']
                ) for r in records]

                execute_values(
                    cursor,
                    """
                    INSERT INTO raw.eia_prices (
                        series_id, period, value, area_name, area_code,
                        product_name, product_code, process_name, process_code,
                        unit, frequency, dataset
                    ) VALUES %s
                    ON CONFLICT (series_id, period) DO NOTHING
                    """,
                    values
                )

            conn.commit()
            logger.info(f"Stored {len(records)} EIA records in database")

        except Exception as e:
            logger.error(f"Error storing EIA data: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def store_enrichment_data(self, data: Dict[str, Any]) -> None:
        """Store enrichment data in database"""
        conn = None
        try:
            conn = psycopg2.connect(**self.db_config)
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO raw.energy_market_context (
                        period, area_code, wti_crude_price_usd, brent_crude_price_usd,
                        crude_spread, refinery_utilization_rate, refinery_outage_index,
                        gasoline_inventory_million_barrels, supply_disruption_index,
                        regional_demand_index, vehicle_miles_traveled_index,
                        avg_temperature_c, heating_degree_days, cooling_degree_days,
                        pipeline_utilization_rate, shipping_cost_index,
                        energy_volatility_index, speculative_pressure_index,
                        hurricane_risk_index, geopolitical_risk_index
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (period, area_code) DO NOTHING
                    """,
                    (
                        data['period'], data['area_code'], data['wti_crude_price_usd'],
                        data['brent_crude_price_usd'], data['crude_spread'],
                        data['refinery_utilization_rate'], data['refinery_outage_index'],
                        data['gasoline_inventory_million_barrels'], data['supply_disruption_index'],
                        data['regional_demand_index'], data['vehicle_miles_traveled_index'],
                        data['avg_temperature_c'], data['heating_degree_days'],
                        data['cooling_degree_days'], data['pipeline_utilization_rate'],
                        data['shipping_cost_index'], data['energy_volatility_index'],
                        data['speculative_pressure_index'], data['hurricane_risk_index'],
                        data['geopolitical_risk_index']
                    )
                )

            conn.commit()
            logger.info(f"Stored enrichment data for {data['area_code']} on {data['period']}")

        except Exception as e:
            logger.error(f"Error storing enrichment data: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()