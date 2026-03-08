select
    period,
    area_code,
    count(*) as record_count
from {{ ref('fact_gasoline_prices') }}
group by period, area_code
having count(*) > 1
