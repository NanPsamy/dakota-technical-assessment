# Reports

Generate automated reports from the analytics data.

## Requirements

Create relevant reports of your choice, below are some examples, points for creativity (spin up Metabase and reports there?):

1. **Excel Report** - Metrics dashboard with charts and tables
2. **Jupyter Notebook** - Exploratory analysis with visualizations
3. **PDF Report** - Executive summary

## What We're Looking For

- Automated generation (triggered by orchestrator)
- Meaningful insights and visualizations
- Professional presentation
- Reproducible outputs

The reports should demonstrate the value of your data pipeline.

## Implemented Automated Report

The orchestrator generates a markdown report with insights and visualizations:

- Report: `reports/output/pipeline_health_report.md`
- PDF: `reports/output/pipeline_health_report.pdf`
- Figures:
	- `reports/output/figures/weekly_trend.png`
	- `reports/output/figures/top_areas_avg_price.png`
	- `reports/output/figures/gasoline_vs_vehicle_miles_weekly_bar.png`

The report includes:

- Executive KPI insights (latest period average price, top-priced region)
- Correlation diagnostics (gasoline vs WTI, demand, volatility)
- Data volume/health row counts
- Embedded charts for trend, ranking, and relationship analysis

Generate it manually:

```bash
cd orchestration
.venv\\Scripts\\python.exe scripts\\generate_reports.py

# Generate PDF version (ReportLab)
.venv\\Scripts\\python.exe scripts\\generate_pdf_report.py
```
