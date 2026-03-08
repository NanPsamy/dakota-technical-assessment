# Orchestration

Implement workflow orchestration for the data pipeline.

## Requirements

Choose and implement an orchestration tool to manage:
- Data ingestion from public data source or EIA (daily batch?)
- Data ingestion from FastAPI service (frequent/streaming?)
- dbt transformations
- Data quality checks
- Report generation
- Error handling and retries

## Tool Choice

- **Prefect** is used for orchestration because this project is Python-first, containerized, and requires quick scheduling/retry setup without heavyweight platform overhead.

See `orchestration/docs/decisions.md` for decision trade-offs.

## Implemented Workflows

All flows are implemented in `orchestration/flows.py`.

- `daily-eia-ingestion-flow`
	- Ensures `postgres` and `api` services are up.
	- Runs `docker compose up ingestion --abort-on-container-exit --exit-code-from ingestion` to ingest EIA prices and enrichment.

- `frequent-api-ingestion-flow`
	- Ensures core services are up.
	- Runs `scripts/api_enrichment_only.py` to refresh enrichment frequently for recent area codes.

- `dbt-build-flow`
	- Runs `dbt run --profiles-dir .` in `dbt/`.

- `dbt-quality-check-flow`
	- Runs `dbt test --profiles-dir .` in `dbt/`.

- `report-generation-flow`
	- Runs `scripts/generate_reports.py` and writes `reports/output/pipeline_health_report.md`.

- `pdf-report-generation-flow`
	- Runs `scripts/generate_reports.py` first, then `scripts/generate_pdf_report.py`.
	- Writes `reports/output/pipeline_health_report.md` and `reports/output/pipeline_health_report.pdf`.

- `end-to-end-daily-flow`
	- Executes ingestion -> dbt run -> dbt test -> report generation sequentially.

## Schedules

Deployments are served with the following cron schedules:

- Daily EIA ingestion: `0 2 * * *`
- Frequent API enrichment ingestion: `*/30 * * * *`
- dbt transformations: `10 * * * *`
- Data quality checks: `20 * * * *`
- Report generation: `0 6 * * *`
- PDF report generation: `0 8 * * *`
- End-to-end daily DAG: `30 6 * * *`

## Setup

```bash
cd orchestration
python -m venv .venv
.venv\\Scripts\\activate
pip install -e .
```

## Run Locally

Run one flow manually:

```bash
cd orchestration
python -c "from flows import end_to_end_daily_flow; end_to_end_daily_flow()"
```

Serve all scheduled deployments:

```bash
cd orchestration
python flows.py
```

## Run as Container

Build and start only the orchestrator:

```bash
docker compose up -d orchestration
```

View orchestrator logs:

```bash
docker compose logs -f orchestration
```

Stop orchestrator:

```bash
docker compose stop orchestration
```

Notes:

- The orchestrator container mounts the full repository at `/workspace`.
- It also mounts `/var/run/docker.sock` so Prefect tasks can execute `docker compose` commands.
- dbt commands run from `/workspace/dbt` with `--profiles-dir .`.

## Notes

- Task-level retries are configured for ingestion, dbt, and reporting tasks.
- Commands auto-detect local executables (`dbt/.venv/Scripts/dbt.exe`, `orchestration/.venv/Scripts/python.exe`) with shell fallbacks.
