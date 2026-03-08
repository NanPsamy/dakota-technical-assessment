import os
import sys
from datetime import date
from pathlib import Path
from typing import List

import psycopg2


ROOT = Path(__file__).resolve().parents[2]
INGESTION_DIR = ROOT / "ingestion"
if str(INGESTION_DIR) not in sys.path:
    sys.path.append(str(INGESTION_DIR))

from fastapi_client import FastAPIClient  # noqa: E402
from database_writer import DatabaseWriter  # noqa: E402


def get_db_config() -> dict:
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "database": os.getenv("DB_NAME", "energy_analytics"),
        "user": os.getenv("DB_USER", "energy_user"),
        "password": os.getenv("DB_PASSWORD", "energy_password"),
    }


def fetch_recent_area_codes(limit: int = 100) -> List[str]:
    db_config = get_db_config()
    sql = """
        select distinct area_code
        from raw.eia_prices
        where area_code is not null
        order by area_code
        limit %s
    """

    with psycopg2.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, (limit,))
            rows = cursor.fetchall()
    return [r[0] for r in rows]


def run() -> None:
    api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    area_limit = int(os.getenv("API_ENRICH_AREA_LIMIT", "100"))
    target_date = os.getenv("API_ENRICH_PERIOD", date.today().isoformat())

    db_config = get_db_config()
    api_client = FastAPIClient(api_base_url)
    db_writer = DatabaseWriter(db_config)

    area_codes = fetch_recent_area_codes(limit=area_limit)

    for area_code in area_codes:
        payload = api_client.fetch_enrichment(area_code, target_date)
        db_writer.store_enrichment_data(payload)


if __name__ == "__main__":
    run()
