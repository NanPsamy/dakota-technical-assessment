select
    series_id,
    period,
    count(*) as record_count
from {{ ref('stg_eia_prices') }}
group by series_id, period
having count(*) > 1
