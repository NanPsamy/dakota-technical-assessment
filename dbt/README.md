# dbt Transformation Layer

Transforms raw ingestion tables into analytics-ready models using a layered dbt pipeline.

## Implementation

### Architecture
- `raw` schema is the source layer populated by ingestion.
- `staging` schema contains cleaned, conformed models.
- `marts` schema contains analytics and ML-ready models.

### Model Flow
- `raw.eia_prices` -> `staging.stg_eia_prices`
- `staging.stg_eia_prices` + `raw.energy_market_context` -> `marts.fact_gasoline_prices`
- `marts.fact_gasoline_prices` -> `marts.energy_market_summary`
- `marts.fact_gasoline_prices` -> `marts.price_driver_features`

### Materialization Strategy
- Staging and fact models are incremental with unique keys for efficient reruns.
- Summary model is table materialized (full rebuild on run).
- Feature model is incremental keyed by `(period, area_code)`.

### Data Quality
- Source definitions are in `models/schema.yml`.
- Model tests include critical `not_null` and `unique` assertions on key columns.

## Setup

### Python virtual environment (pip)
```bash
python -m venv venv
venv\\Scripts\\activate
pip install dbt-core dbt-postgres
```

### Profile and target
- Configure `profiles.yml` for PostgreSQL credentials.
- Ensure dbt uses the project profiles directory when running locally:
	- PowerShell: `$env:DBT_PROFILES_DIR='C:\\path\\to\\dakota-technical-assessment\\dbt'`

## Run

```bash
dbt debug
dbt run
dbt test
```

## Files

- `dbt_project.yml`: Project config, model paths, schema/materialization settings.
- `profiles.yml`: PostgreSQL connection profile.
- `models/staging/stg_eia_prices.sql`: Staging transformation.
- `models/marts/fact_gasoline_prices.sql`: Core fact model.
- `models/marts/energy_market_summary.sql`: Regional summary mart.
- `models/marts/price_driver_features.sql`: ML features mart.
- `models/**/schema.yml`: Source definitions, tests, and documentation.
