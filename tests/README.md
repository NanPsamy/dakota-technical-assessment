# System-Wide Test Plan

This folder outlines best-practice, system-level validation for the full Dakota pipeline.

## Scope

- Infrastructure and service health
- Ingestion correctness and idempotency
- Transformation quality (dbt)
- Orchestration schedule/flow behavior
- Reporting artifact generation (markdown + PDF + figures)
- Startup script behavior (`run.bat`)

## Recommended Test Layers

1. **Smoke tests**
   - `docker compose up` succeeds.
   - `postgres`, `api`, and `orchestration` become healthy.

2. **Pipeline integration tests**
   - Ingestion writes non-zero rows to raw tables.
   - dbt models materialize expected tables with non-zero counts.
   - dbt tests all pass.

3. **Idempotency tests**
   - Re-running ingestion does not create duplicate key conflicts.
   - Re-running dbt incremental models succeeds without duplicate key violations.
   - Re-running `run.bat` skips completed setup unless `--force`.

4. **Reporting tests**
   - Markdown report generated with expected sections.
   - Figures exist and are refreshed.
   - PDF report generated and includes chart assets.

5. **Failure-path tests**
   - Simulate unavailable API or DB and confirm script exits `1`.
   - Confirm errors and compose logs are captured to `logs/run.log`.

## Operational Commands

Run core system checks manually:

```bash
# service topology
 docker compose ps

# ingestion batch
 docker compose up ingestion --abort-on-container-exit --exit-code-from ingestion

# dbt quality
 dbt run --project-dir dbt --profiles-dir dbt
 dbt test --project-dir dbt --profiles-dir dbt

# report artifacts
 python orchestration/scripts/generate_reports.py
 python orchestration/scripts/generate_pdf_report.py
```

## CI Recommendation

For a productionized extension, add CI jobs for:

- lint + static checks
- dbt compile/run/test in ephemeral DB
- orchestration flow smoke run
- artifact existence checks for reports
