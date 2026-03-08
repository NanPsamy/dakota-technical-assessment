{{ config(
    materialized='incremental',
    unique_key=['period','area_code'],
    incremental_strategy='delete+insert'
) }}

select
    period,
    area_code,
    gasoline_price,
    wti_crude_price_usd,
    refinery_utilization_rate,
    gasoline_inventory_million_barrels,
    regional_demand_index,
    vehicle_miles_traveled_index,
    avg_temperature_c,
    hurricane_risk_index,
    energy_volatility_index,
    current_timestamp as created_at
from {{ ref('fact_gasoline_prices') }}
