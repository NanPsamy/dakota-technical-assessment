# Orchestration Decision

## Decision

Use **Prefect** as the orchestration framework for this pipeline.

## Why Prefect

- Python-native orchestration fits an existing Python + dbt + Docker workflow.
- Faster implementation and lower operational overhead than Airflow for this project size.
- Built-in retries/scheduling and straightforward local execution for assessment/demo workflows.
- Easy wrapping of existing shell commands (`docker compose`, `dbt run`, `dbt test`).

## Trade-offs

- Airflow has stronger enterprise ecosystem adoption and UI familiarity in some teams.
- Dagster provides richer software-defined asset patterns and lineage semantics.
- Prefect is the better balance here for speed, maintainability, and minimal platform complexity.

## Workflow Design

- Daily batch EIA ingestion.
- Frequent enrichment refresh from FastAPI.
- Hourly dbt transformations and quality checks.
- Daily report generation.
- Optional end-to-end daily DAG for a single managed pipeline run.

## Reliability Controls

- Task retries with delay for network/command flakiness.
- Health-first orchestration by ensuring core services are running before ingestion tasks.
- Data quality gate through `dbt test` in scheduled flow.
