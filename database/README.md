# Database

Design and implement the database schema for the pipeline.

## Requirements

- Use PostgreSQL or have clear rationale for why you chose something else
- Design schema for raw data storage and transformed analytics
- Include initialization scripts in `init/`
- Document your schema design

## What We're Looking For

- Thoughtful data modeling decisions
- Appropriate use of schemas, indexes, and constraints
- Consideration for time-series data characteristics
- ER diagram or schema documentation in `documentation/`
- Clear rationale for your design choices

**Note:** Any examples or patterns mentioned elsewhere are suggestions only. Make your own informed decisions about schema design, naming, partitioning strategies, etc. We want to see **your** thinking.

## Implementation

### Technology Choice
- **PostgreSQL**: Chosen for its robust support for time-series handling via DATE/TIMESTAMPTZ, analytics capabilities, and integration with dbt and Python tools. It's open-source, scalable, and handles complex schemas well.

### Schema Design
- **Raw Schema**: Stores ingested data as-is from EIA API and FastAPI enrichment.
  - `eia_prices`: Weekly petroleum prices with detailed metadata.
  - `energy_market_context`: Synthetic enrichment data with market signals.
- **Staging Schema**: Cleaned models built by dbt.
  - `stg_eia_prices`: Processed EIA prices with null `gasoline_price` records filtered out.
- **Marts Schema**: Final reporting and ML datasets.
  - `fact_gasoline_prices`: Detailed fact table with enrichment.
  - `energy_market_summary`: Regional summaries.
  - `price_driver_features`: ML-ready features.

### Data Quality Alignment (dbt + Database)
- `staging.stg_eia_prices` uses a composite primary key `(series_id, period)`; uniqueness is validated at this key level.
- `gasoline_price` is modeled as required in staging and downstream marts (`fact_gasoline_prices`, `price_driver_features`).
- Timestamp audit columns in marts (`created_at`, `last_updated`) are treated as required metadata columns.

### Time-Series Considerations
- Used `DATE` for period fields (weekly granularity) to handle time zones implicitly.
- Indexed on `period` for efficient range queries (e.g., last 6 months).
- Added constraints to prevent future dates and ensure data validity.
- For larger scales, consider partitioning by month/year, but kept simple for this assessment.

### Files
- `init/01_schema.sql`: Database initialization script with layered schemas.
- `documentation/er_diagram.md`: ER diagram and rationale.
