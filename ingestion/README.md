# Data Ingestion

Build ingestion clients for fetching data from the EIA API and the FastAPI enrichment endpoint.

## Requirements

1. **EIA API Client** - Fetch petroleum price data from EIA's public API
   - API docs: https://www.eia.gov/opendata/
   - Free API key required: https://www.eia.gov/opendata/register.php
   - Dataset: Weekly gasoline prices from petroleum/pri/gnd

2. **FastAPI Client** - Fetch enrichment data from the local API service

## What We're Looking For

- Error handling and retries (using tenacity)
- Comprehensive logging
- Rate limiting awareness
- Data validation with Pydantic
- Database storage with conflict resolution
- Environment variable configuration

## Implementation

### Files
- `pyproject.toml`: uv dependency management
- `config.py`: Configuration and environment variables
- `eia_client.py`: EIA API client with data fetching
- `fastapi_client.py`: FastAPI enrichment service client
- `database_writer.py`: Database operations for storing data
- `ingest.py`: Main ingestion orchestrator

### Environment Variables
Create a `.env` file with:
```
EIA_API_KEY=your_api_key_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=energy_analytics
DB_USER=energy_user
DB_PASSWORD=energy_password
API_BASE_URL=http://localhost:8000
```

### Running Locally
```bash
# Install dependencies and sync environment
uv sync

# Run the ingestion script
uv run python ingest.py

# Or run with environment variables
EIA_API_KEY=your_key uv run python ingest.py
```

### Docker
```bash
docker build -t ingestion .
docker run --env-file .env ingestion
```

### Features
- **EIA Data**: Fetches weekly petroleum prices with pagination support
- **Enrichment**: Calls API for each unique area code from EIA data
- **Validation**: Pydantic models ensure data quality
- **Retries**: Exponential backoff for API failures
- **Storage**: Upsert logic prevents duplicates
- **Logging**: Detailed logs for monitoring
