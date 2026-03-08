# System Test Cases

## ST-01: First-Time Bootstrap

- **Goal**: Validate clean-environment startup.
- **Command**: `run.bat`
- **Expected**:
  - `.env` created from `.env.example`.
  - dependencies installed.
  - containers built and core services started.
  - ingestion, dbt run, dbt test, markdown report, and PDF report complete.

## ST-02: Subsequent Idempotent Run

- **Goal**: Ensure safe repeated execution.
- **Command**: `run.bat`
- **Expected**:
  - setup/build steps are skipped where state markers exist.
  - no duplicate-key failures in ingestion/dbt.
  - script exits with `0`.

## ST-03: Force Rebuild/Rerun

- **Goal**: Validate explicit rerun behavior.
- **Command**: `run.bat --force`
- **Expected**:
  - containers rebuilt.
  - full pipeline executes end-to-end.

## ST-04: Service Health

- **Goal**: Confirm health-check based readiness.
- **Command**: `docker compose ps`
- **Expected**:
  - `postgres`, `api`, `orchestration` show healthy/running state.

## ST-05: Data Volume Sanity

- **Goal**: Confirm non-zero data after pipeline run.
- **Checks**:
  - `raw.eia_prices` > 0
  - `staging.stg_eia_prices` > 0
  - `marts.fact_gasoline_prices` > 0

## ST-06: dbt Data Quality

- **Goal**: Ensure transformation quality gate passes.
- **Commands**:
  - `dbt run --project-dir dbt --profiles-dir dbt`
  - `dbt test --project-dir dbt --profiles-dir dbt`
- **Expected**: all tests pass.

## ST-07: Reporting Artifacts

- **Goal**: Validate outputs and figures.
- **Expected files**:
  - `reports/output/pipeline_health_report.md`
  - `reports/output/pipeline_health_report.pdf`
  - `reports/output/figures/weekly_trend.png`
  - `reports/output/figures/top_areas_avg_price.png`
  - `reports/output/figures/gasoline_vs_wti_scatter.png`

## ST-08: Error Handling

- **Goal**: Validate script failure behavior.
- **Method**: stop API/DB and run pipeline.
- **Expected**:
  - script exits with code `1`
  - `logs/run.log` contains error context and docker compose logs.
