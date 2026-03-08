# System Architecture And Design

## System Design Overview

This project implements a layered data platform for weekly U.S. gasoline analytics. The architecture is organized as modular services and transformation layers:

- `api/`: FastAPI synthetic enrichment service.
- `ingestion/`: data ingestion clients and database write path.
- `database/`: PostgreSQL schemas, constraints, indexes, and initialization SQL.
- `dbt/`: transformation and quality layer from raw to analytics-ready marts.
- `orchestration/`: Prefect flows/deployments coordinating all modules.
- `reports/`: automated markdown and PDF reporting with visualizations.

The runtime topology is containerized with Docker Compose (`postgres`, `api`, `ingestion`, `orchestration`).

## Technology Choices And Why

### PostgreSQL

- Chosen for reliable transactional writes and strong analytical SQL support.
- Suits time-series weekly data (`DATE`, `TIMESTAMPTZ`) and strict constraints.
- Supports layered schemas (`raw`, `staging`, `marts`) for data lifecycle separation.

### FastAPI + Pydantic

- FastAPI gives simple, strongly-typed API contracts and automatic OpenAPI docs.
- Pydantic ensures synthetic enrichment payload quality and type safety.

### Ingestion (Python + requests + tenacity)

- `requests` handles EIA and service calls.
- `tenacity` adds retry/backoff resilience for network and transient failures.
- Explicit type normalization and validation reduce downstream data quality issues.

### dbt (dbt-postgres)

- Clear SQL-first transformation framework.
- Declarative tests (`not_null`, `unique`, singular uniqueness checks).
- Incremental materializations and key-based idempotency improve runtime performance.

### Prefect

- Lightweight, Python-native orchestration for local/containerized workflows.
- Native retries, schedules, task decomposition, and deployment serving.
- Good fit for mixed command tasks (`docker compose`, `dbt`, report scripts).

### Reporting (matplotlib + ReportLab)

- Markdown report for quick inspection and versionable outputs.
- PNG figures for trend/ranking/relationship analytics.
- ReportLab PDF for executive-friendly artifact generation.

## Data Flow

1. **Source ingestion**
   - EIA petroleum weekly data fetched and validated.
   - Raw records written to `raw.eia_prices`.

2. **Enrichment ingestion**
   - For area codes in source data, synthetic enrichment fetched from FastAPI.
   - Written to `raw.energy_market_context`.

3. **Transformation (dbt)**
   - `raw` -> `staging.stg_eia_prices` (cleaning, filtering null prices).
   - `staging + raw enrichment` -> `marts.fact_gasoline_prices`.
   - `fact` -> `marts.energy_market_summary` and `marts.price_driver_features`.

4. **Data quality checks**
   - dbt test suite validates key nullability, uniqueness, and table assumptions.

5. **Reporting**
   - Markdown report generated with KPI insights + charts.
   - PDF report generated daily from latest markdown/chart data inputs.

6. **Orchestration schedules**
   - Daily EIA ingestion.
   - Frequent API enrichment refresh.
   - Scheduled dbt run/test.
   - Scheduled markdown and PDF report generation (PDF at 8AM).

## Scalability Considerations

### Compute and orchestration

- Flows are taskized with retries and can be split across workers later.
- Frequency-based separation (daily batch vs frequent enrichment) reduces contention.

### Database and transformations

- Indexed keys on period/area/series support filtering and joins.
- Incremental dbt models avoid full refresh costs for every run.
- Composite keys (`series_id, period`; `period, area_code`) preserve idempotency.

### Data growth

- Current design supports moderate growth with straightforward extensions:
  - partition large fact tables by period,
  - archive old raw snapshots,
  - tune materializations and model schedules.

### Reliability and observability

- Health checks for core services.
- End-to-end script logging (`logs/run.log`) and state markers for idempotent runs.
- Prefect retries + scheduled deployments improve operational stability.

## Architecture Diagram Assets

- Database ER diagram markdown source: `database/documentation/er_diagram.md`
- PNG export used for submission docs: `docs/er_diagram.png`
