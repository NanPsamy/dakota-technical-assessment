{{ config(
    materialized='incremental',
    unique_key=['series_id','period']
) }}

with source as (
    select
        series_id,
        period::date as period,
        value::numeric(10,4) as gasoline_price,
        area_code,
        area_name,
        product_code,
        product_name,
        process_code,
        process_name,
        unit,
        frequency
    from {{ source('raw','eia_prices') }}
)

select
    *,
    CURRENT_TIMESTAMP as processed_at
from source
where gasoline_price is not null