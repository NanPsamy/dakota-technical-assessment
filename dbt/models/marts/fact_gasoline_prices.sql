{{ config(
    materialized='incremental',
    unique_key=['period','area_code'],
    incremental_strategy='delete+insert'
) }}

with prices as (
    select
        period,
        area_code,
        max(area_name) as area_name,
        avg(gasoline_price) as gasoline_price
    from {{ ref('stg_eia_prices') }}
    where area_code is not null
    group by period, area_code
),

context as (
    select
        period,
        area_code,
        wti_crude_price_usd,
        brent_crude_price_usd,
        crude_spread,
        refinery_utilization_rate,
        gasoline_inventory_million_barrels,
        regional_demand_index,
        vehicle_miles_traveled_index,
        avg_temperature_c,
        energy_volatility_index,
        hurricane_risk_index
    from {{ source('raw','energy_market_context') }}
)

select
    p.period,
    p.area_code,
    p.area_name,
    p.gasoline_price,
    c.wti_crude_price_usd,
    c.brent_crude_price_usd,
    c.crude_spread,
    c.refinery_utilization_rate,
    c.gasoline_inventory_million_barrels,
    c.regional_demand_index,
    c.vehicle_miles_traveled_index,
    c.avg_temperature_c,
    c.energy_volatility_index,
    c.hurricane_risk_index,
    current_timestamp as created_at
from prices p
left join context c
  on p.period = c.period
  and p.area_code = c.area_code
