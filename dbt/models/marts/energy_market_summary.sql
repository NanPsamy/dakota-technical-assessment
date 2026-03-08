{{ config(
    materialized='table'
) }}

with fact_data as (
    select
        area_code,
        area_name,
        gasoline_price,
        wti_crude_price_usd,
        regional_demand_index,
        refinery_utilization_rate
    from {{ ref('fact_gasoline_prices') }}
)

select
    area_code,
    area_name,
    round(avg(gasoline_price)::numeric, 4) as avg_price,
    round(max(gasoline_price)::numeric, 4) as peak_price,
    round(avg(wti_crude_price_usd)::numeric, 2) as avg_crude_price,
    round(avg(regional_demand_index)::numeric, 3) as avg_demand,
    round(avg(refinery_utilization_rate)::numeric, 2) as avg_refinery_utilization,
    current_timestamp as last_updated
from fact_data
group by area_code, area_name
