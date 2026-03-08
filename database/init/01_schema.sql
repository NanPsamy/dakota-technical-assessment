-- =====================================================
-- ENERGY ANALYTICS DATA PIPELINE SCHEMA
-- =====================================================
-- Layers:
-- raw -> staging -> marts
-- =====================================================

-- =====================================================
-- CREATE SCHEMAS
-- =====================================================

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;

-- =====================================================
-- RAW LAYER
-- Immutable landing tables for API ingestion and enrichment data
-- =====================================================

-- Raw EIA gasoline price dataset
CREATE TABLE IF NOT EXISTS raw.eia_prices (
    id BIGSERIAL PRIMARY KEY,
    series_id TEXT NOT NULL,
    period DATE NOT NULL,   -- Weekly period
    value NUMERIC(10,4),    -- Price value
    area_name TEXT,
    area_code TEXT,
    product_name VARCHAR(100) NOT NULL,  -- e.g., 'Gasoline', 'Diesel'
    product_code TEXT,
    process_name TEXT,
    process_code TEXT,
    unit VARCHAR(50),  -- e.g., 'dollars per gallon'
    frequency TEXT,
    dataset TEXT DEFAULT 'petroleum/pri/gnd',
    ingestion_timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_eia_prices_series_period UNIQUE (series_id, period)
);

-- Enrichment dataset for synthetic energy market context signals
CREATE TABLE IF NOT EXISTS raw.energy_market_context (
    id BIGSERIAL PRIMARY KEY,
    period DATE NOT NULL,   -- Corresponding period (weekly)
    area_code TEXT NOT NULL,
    wti_crude_price_usd NUMERIC(10,2),
    brent_crude_price_usd NUMERIC(10,2),
    crude_spread NUMERIC(8,2),
    refinery_utilization_rate NUMERIC(5,2),
    refinery_outage_index NUMERIC(6,3),
    gasoline_inventory_million_barrels NUMERIC(10,2),
    supply_disruption_index NUMERIC(6,3),
    regional_demand_index NUMERIC(6,3),
    vehicle_miles_traveled_index NUMERIC(6,3),
    avg_temperature_c NUMERIC(5,2),
    heating_degree_days NUMERIC(6,2),
    cooling_degree_days NUMERIC(6,2),
    pipeline_utilization_rate NUMERIC(5,2),
    shipping_cost_index NUMERIC(6,3),
    energy_volatility_index NUMERIC(6,3),
    speculative_pressure_index NUMERIC(6,3),
    hurricane_risk_index NUMERIC(6,3),
    geopolitical_risk_index NUMERIC(6,3),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_period_not_future CHECK (period <= CURRENT_DATE),
    CONSTRAINT chk_rates_range CHECK (refinery_utilization_rate BETWEEN 0 AND 100),
    CONSTRAINT uq_energy_context_period_area UNIQUE (period, area_code)
);

-- Indexes for raw layer tables
CREATE INDEX IF NOT EXISTS idx_raw_prices_period ON raw.eia_prices (period);
CREATE INDEX IF NOT EXISTS idx_raw_prices_series ON raw.eia_prices (series_id);
-- unique constraint already provides index on (series_id, period) so no separate index needed
CREATE INDEX IF NOT EXISTS idx_raw_prices_area ON raw.eia_prices (area_code);
CREATE INDEX IF NOT EXISTS idx_energy_context_period_area ON raw.energy_market_context (period, area_code);

-- =====================================================
-- STAGING LAYER
-- Cleaned models typically built by dbt
-- =====================================================

CREATE TABLE IF NOT EXISTS staging.stg_eia_prices (
    series_id TEXT NOT NULL,
    period DATE NOT NULL,
    gasoline_price NUMERIC(10,4) NOT NULL,
    area_code TEXT,
    area_name TEXT,
    product_code TEXT,
    product_name TEXT,
    process_code TEXT,
    process_name TEXT,
    unit TEXT,
    frequency TEXT,
    processed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    -- Composite key supports weekly snapshots per series_id.
    PRIMARY KEY (series_id, period),
    CONSTRAINT chk_gasoline_price_positive CHECK (gasoline_price >= 0)
);

CREATE INDEX IF NOT EXISTS idx_stg_prices_period ON staging.stg_eia_prices (period);

-- =====================================================
-- ANALYTICS MARTS
-- Final reporting and ML datasets
-- =====================================================

-- Fact table joining price + enrichment features
CREATE TABLE IF NOT EXISTS marts.fact_gasoline_prices (
    period DATE NOT NULL,
    area_code TEXT NOT NULL,
    area_name TEXT,
    gasoline_price NUMERIC(10,4) NOT NULL,
    wti_crude_price_usd NUMERIC(10,2),
    brent_crude_price_usd NUMERIC(10,2),
    crude_spread NUMERIC(8,2),
    refinery_utilization_rate NUMERIC(5,2),
    gasoline_inventory_million_barrels NUMERIC(10,2),
    regional_demand_index NUMERIC(6,3),
    vehicle_miles_traveled_index NUMERIC(6,3),
    avg_temperature_c NUMERIC(5,2),
    energy_volatility_index NUMERIC(6,3),
    hurricane_risk_index NUMERIC(6,3),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (period, area_code),
    CONSTRAINT chk_fact_price_positive CHECK (gasoline_price >= 0),
    CONSTRAINT chk_fact_rates_range CHECK (refinery_utilization_rate BETWEEN 0 AND 100)
);

CREATE INDEX IF NOT EXISTS idx_fact_prices_period ON marts.fact_gasoline_prices (period);
CREATE INDEX IF NOT EXISTS idx_fact_prices_area ON marts.fact_gasoline_prices (area_code);

-- Regional summary analytics mart
CREATE TABLE IF NOT EXISTS marts.energy_market_summary (
    area_code TEXT PRIMARY KEY,
    area_name TEXT,
    avg_price NUMERIC(10,4) NOT NULL,
    peak_price NUMERIC(10,4),
    avg_crude_price NUMERIC(10,2),
    avg_demand NUMERIC(6,3),
    avg_refinery_utilization NUMERIC(5,2),
    last_updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_summary_price_positive CHECK (avg_price >= 0 AND peak_price >= 0)
);

-- ML feature table for modeling price drivers
CREATE TABLE IF NOT EXISTS marts.price_driver_features (
    period DATE NOT NULL,
    area_code TEXT NOT NULL,
    gasoline_price NUMERIC(10,4) NOT NULL,
    wti_crude_price_usd NUMERIC(10,2),
    refinery_utilization_rate NUMERIC(5,2),
    gasoline_inventory_million_barrels NUMERIC(10,2),
    regional_demand_index NUMERIC(6,3),
    vehicle_miles_traveled_index NUMERIC(6,3),
    avg_temperature_c NUMERIC(5,2),
    hurricane_risk_index NUMERIC(6,3),
    energy_volatility_index NUMERIC(6,3),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (period, area_code),
    CONSTRAINT chk_features_price_positive CHECK (gasoline_price >= 0)
);

CREATE INDEX IF NOT EXISTS idx_features_period ON marts.price_driver_features (period);
