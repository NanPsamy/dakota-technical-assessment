# Technical Decisions And Rationale

This document summarizes major technical decisions across modules, trade-offs considered, and rationale.

## 1) API Module

### Decision
Use FastAPI with Pydantic models to generate synthetic market context signals.

### Why
- Fast implementation, strong typing, clear contracts.
- Auto-generated interactive documentation for integration validation.

### Trade-off
- Synthetic data is not real market feed quality, but enables deterministic enrichment during assessment scope.

## 2) Ingestion Module

### Decision
Implement modular ingestion (`config.py`, `eia_client.py`, `fastapi_client.py`, `database_writer.py`, `ingest.py`) with retries and validation.

### Why
- Separation of concerns supports maintainability and testability.
- Retry + logging pattern handles transient API/network issues.
- Explicit coercion avoids type errors in storage and transformations.

### Trade-off
- More files/abstractions than a single script, but better long-term maintainability.

## 3) Database Model

### Decision
Use layered schemas: `raw`, `staging`, `marts` with strict constraints and keys.

### Why
- Raw layer preserves source/enrichment history and replayability.
- Staging layer standardizes cleaned entities.
- Marts serve analytics/reporting and feature consumption.

### Key constraints
- `raw.eia_prices`: unique `(series_id, period)` for conflict-safe upserts.
- `raw.energy_market_context`: unique `(period, area_code)` for idempotent enrichment writes.
- Staging/marts enforce required metrics and positive-range checks.

### Trade-off
- More schema management complexity, but clearer data contracts and quality boundaries.

## 4) dbt Transformations

### Decision
Use incremental models for staging/fact/features, table materialization for summary, and comprehensive tests.

### Why
- Incremental reduces compute for recurring schedules.
- Summary table remains simple and reliable for reporting workloads.
- Tests guard key assumptions (nullability, uniqueness, composite-key constraints).

### Adjustments made
- Updated model logic to avoid duplicate key conflicts on reruns.
- Aligned model outputs with table columns (`created_at`, `last_updated`) to prevent runtime errors.

## 5) Orchestration

### Decision
Choose Prefect with multiple scheduled flows and one end-to-end daily flow.

### Why
- Python-native orchestration with low operational overhead.
- Easy wrapping of existing command-driven pipeline tasks.
- Built-in scheduling/retries maps directly to assessment requirements.

### Schedule strategy
- Daily EIA ingestion.
- Frequent API enrichment refresh.
- Scheduled dbt run and dbt test.
- Markdown reports and PDF reports (daily PDF at 8AM).

### Trade-off
- Less enterprise ecosystem footprint than Airflow, but faster delivery and simpler local setup.

## 6) Reporting

### Decision
Generate markdown + PNG figures + PDF (ReportLab).

### Why
- Markdown is diff-friendly and easy to inspect.
- PNG charts provide quick visual insight.
- PDF supports executive consumption and submission artifact completeness.

### Visualization decisions
- Weekly gasoline trend as line graph.
- Top regions by average gasoline price.
- Gasoline vs WTI scatter relationship for comparative insight.

## 7) Containerization

### Decision
Containerize API, ingestion, database, and orchestration in Docker Compose.

### Why
- Reproducible environment for assessment validation.
- Simplifies bring-up and dependency control.

### Notable implementation decision
- Orchestrator mounts Docker socket to trigger compose tasks from Prefect jobs.

## 8) Startup Automation

### Decision
Use root `run.bat` as idempotent operational entry point.

### Why
- Handles first-time setup and subsequent runs with skip logic.
- Centralizes clear logging and failure behavior.
- Produces deterministic end-to-end run for reviewers.

### Behavior
- Creates `.env` if missing.
- Ensures dependencies and containers are prepared.
- Runs ingestion -> dbt run -> dbt test -> report generation.
- On failure logs and exits with code `1`.

## 9) Testing Strategy

### Decision
Combine dbt data tests with system-level runbook tests under `tests/`.

### Why
- dbt tests verify dataset integrity and model assumptions.
- system-level checks validate orchestration, service health, idempotency, and artifacts.

### Trade-off
- Primarily integration-focused for this scope; can be extended with unit/integration CI as next step.
