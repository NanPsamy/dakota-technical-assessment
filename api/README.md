# FastAPI Fake Data Service

Build a FastAPI service that generates synthetic enrichment data for the pipeline.

## Requirements

- Create a FastAPI application that serves synthetic data
- Use `uv` for dependency management
- Containerize within Docker
- Include health check endpoint
- Generate data types relevant to your analysis (your choice for what makes sense)

## What We're Looking For

- Clean API design
- Proper data models
- Reasonable synthetic data generation
- Good error handling
- API documentation (FastAPI auto-docs?)
- Containerization

The data you generate should enrich the source data in meaningful ways.

## Implementation

### Dependencies
- Managed with `uv` via `pyproject.toml`
- Key packages: FastAPI, Uvicorn, Pydantic, Faker, Numpy

### Endpoints
- `GET /`: Root endpoint
- `GET /health`: Health check
- `GET /enrich/{area_code}`: Generate enrichment data for area and optional period
- `POST /enrich/batch`: Generate data for multiple periods/areas

### Data Model
Matches `raw.energy_market_context` schema with realistic synthetic generation including:
- Price correlations (WTI vs Brent)
- Seasonal demand patterns
- Temperature-based degree days
- Risk indices with geographic considerations

### Running Locally
```bash
# install dependencies and sync environment
uv sync

# start development server with autoreload
uv run uvicorn main:app --reload

# you can also run tests or scripts inside the same isolated environment:
# uv run python some_script.py
```
### Docker
```bash
docker build -t dakota-api .
docker run -p 8000:8000 dakota-api
```

API docs available at http://localhost:8000/docs
