# Pipeline Health Report

Generated at: 2026-03-08T09:03:34.780505+00:00

## Executive Insights

- Latest period `2026-03-02` average gasoline price is **$3.561**.
- Highest average price region is **CALIFORNIA** at **$4.534**.
- Correlation with WTI price: **-0.086**.
- Correlation with regional demand index: **-0.069**.
- Correlation with energy volatility index: **-0.317**.

## Row Counts

- `staging.stg_eia_prices`: 4957
- `marts.fact_gasoline_prices`: 4957
- `marts.energy_market_summary`: 29
- `marts.price_driver_features`: 4957

## Visualizations

### Weekly Gasoline Price Trend
![Weekly Trend](figures/weekly_trend.png)

### Top Regions by Average Price
![Top Areas](figures/top_areas_avg_price.png)

### Gasoline vs WTI Scatter
![Gasoline vs WTI](figures/gasoline_vs_wti_scatter.png)