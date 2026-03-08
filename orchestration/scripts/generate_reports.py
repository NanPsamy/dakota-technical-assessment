from datetime import datetime, timezone
from pathlib import Path
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import psycopg2


def get_db_config() -> dict:
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "database": os.getenv("DB_NAME", "energy_analytics"),
        "user": os.getenv("DB_USER", "energy_user"),
        "password": os.getenv("DB_PASSWORD", "energy_password"),
    }


def fetch_row_counts(cursor) -> dict:
    query = """
        select 'staging.stg_eia_prices' as table_name, count(*) as cnt from staging.stg_eia_prices
        union all
        select 'marts.fact_gasoline_prices', count(*) from marts.fact_gasoline_prices
        union all
        select 'marts.energy_market_summary', count(*) from marts.energy_market_summary
        union all
        select 'marts.price_driver_features', count(*) from marts.price_driver_features
    """
    cursor.execute(query)
    return {table_name: cnt for table_name, cnt in cursor.fetchall()}


def fetch_weekly_trend(cursor) -> list[tuple]:
    query = """
        select
            period,
            avg(gasoline_price) as avg_gasoline_price
        from marts.fact_gasoline_prices
        group by period
        order by period
    """
    cursor.execute(query)
    return cursor.fetchall()


def fetch_top_areas(cursor, limit: int = 10) -> list[tuple]:
    query = """
        select
            coalesce(area_name, area_code) as area_label,
            avg(gasoline_price) as avg_gasoline_price
        from marts.fact_gasoline_prices
        group by area_code, area_name
        order by avg_gasoline_price desc
        limit %s
    """
    cursor.execute(query, (limit,))
    return cursor.fetchall()


def fetch_price_wti_points(cursor, limit: int = 2000) -> list[tuple]:
    query = """
        select gasoline_price, wti_crude_price_usd
        from marts.fact_gasoline_prices
        where gasoline_price is not null and wti_crude_price_usd is not null
        limit %s
    """
    cursor.execute(query, (limit,))
    return cursor.fetchall()


def fetch_insights(cursor) -> dict:
    insights = {}

    cursor.execute(
        """
        select period, avg(gasoline_price) as avg_price
        from marts.fact_gasoline_prices
        group by period
        order by period desc
        limit 1
        """
    )
    latest = cursor.fetchone()
    if latest:
        insights["latest_period"] = latest[0]
        insights["latest_avg_price"] = float(latest[1]) if latest[1] is not None else None

    cursor.execute(
        """
        select coalesce(area_name, area_code) as area_label, avg(gasoline_price) as avg_price
        from marts.fact_gasoline_prices
        group by area_code, area_name
        order by avg_price desc
        limit 1
        """
    )
    top_area = cursor.fetchone()
    if top_area:
        insights["highest_area"] = top_area[0]
        insights["highest_area_price"] = float(top_area[1]) if top_area[1] is not None else None

    cursor.execute(
        """
        select
            corr(gasoline_price, wti_crude_price_usd) as corr_wti,
            corr(gasoline_price, regional_demand_index) as corr_demand,
            corr(gasoline_price, energy_volatility_index) as corr_volatility
        from marts.fact_gasoline_prices
        where gasoline_price is not null
        """
    )
    corr_row = cursor.fetchone()
    if corr_row:
        insights["corr_wti"] = float(corr_row[0]) if corr_row[0] is not None else None
        insights["corr_demand"] = float(corr_row[1]) if corr_row[1] is not None else None
        insights["corr_volatility"] = float(corr_row[2]) if corr_row[2] is not None else None

    return insights


def fetch_report_data() -> dict:
    db_config = get_db_config()
    payload = {}
    with psycopg2.connect(**db_config) as conn:
        with conn.cursor() as cursor:
            payload["row_counts"] = fetch_row_counts(cursor)
            payload["weekly_trend"] = fetch_weekly_trend(cursor)
            payload["top_areas"] = fetch_top_areas(cursor)
            payload["scatter_points"] = fetch_price_wti_points(cursor)
            payload["insights"] = fetch_insights(cursor)
    return payload


def _ensure_dirs() -> tuple[Path, Path]:
    report_dir = Path(__file__).resolve().parents[2] / "reports" / "output"
    figures_dir = report_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    return report_dir, figures_dir


def _plot_weekly_trend(data: list[tuple], out_path: Path) -> None:
    if not data:
        return

    periods = [row[0] for row in data]
    gasoline = [float(row[1]) if row[1] is not None else None for row in data]

    plt.figure(figsize=(12, 5))
    tick_labels = [str(p) for p in periods]
    if len(tick_labels) > 12:
        step = max(1, len(tick_labels) // 12)
        tick_positions = periods[::step]
        tick_text = tick_labels[::step]
    else:
        tick_positions = periods
        tick_text = tick_labels
    plt.plot(periods, gasoline, color="#2563eb", linewidth=2.2, marker="o", markersize=4, label="Avg Gasoline Price")
    plt.xticks(tick_positions, tick_text, rotation=45, ha="right")
    plt.title("Weekly Trend: Average Gasoline Price")
    plt.xlabel("Period")
    plt.ylabel("USD")
    plt.grid(axis="y", alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def _plot_top_areas(data: list[tuple], out_path: Path) -> None:
    if not data:
        return

    labels = [row[0] for row in data]
    values = [float(row[1]) if row[1] is not None else 0.0 for row in data]

    plt.figure(figsize=(10, 6))
    plt.barh(labels[::-1], values[::-1])
    plt.title("Top 10 Areas by Average Gasoline Price")
    plt.xlabel("Average Gasoline Price (USD)")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def _plot_wti_scatter(data: list[tuple], out_path: Path) -> None:
    if not data:
        return

    gasoline = [float(row[0]) for row in data if row[0] is not None and row[1] is not None]
    wti = [float(row[1]) for row in data if row[0] is not None and row[1] is not None]
    if not gasoline or not wti:
        return

    plt.figure(figsize=(8, 6))
    plt.scatter(wti, gasoline, alpha=0.35, s=12)
    plt.title("Gasoline Price vs WTI Price")
    plt.xlabel("WTI Crude Price (USD)")
    plt.ylabel("Gasoline Price (USD)")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def render_visualizations(data: dict) -> dict:
    report_dir, figures_dir = _ensure_dirs()
    paths = {
        "weekly_trend": figures_dir / "weekly_trend.png",
        "top_areas": figures_dir / "top_areas_avg_price.png",
        "scatter": figures_dir / "gasoline_vs_wti_scatter.png",
    }

    _plot_weekly_trend(data.get("weekly_trend", []), paths["weekly_trend"])
    _plot_top_areas(data.get("top_areas", []), paths["top_areas"])
    _plot_wti_scatter(data.get("scatter_points", []), paths["scatter"])

    return {k: v.relative_to(report_dir) for k, v in paths.items()}


def write_report(data: dict, figure_paths: dict) -> Path:
    report_dir, _ = _ensure_dirs()

    report_path = report_dir / "pipeline_health_report.md"
    row_counts = data.get("row_counts", {})
    insights = data.get("insights", {})

    figure_paths = {k: str(v).replace('\\', '/') for k, v in figure_paths.items()}

    lines = [
        "# Pipeline Health Report",
        "",
        f"Generated at: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Executive Insights",
        "",
    ]

    latest_period = insights.get("latest_period")
    latest_avg_price = insights.get("latest_avg_price")
    highest_area = insights.get("highest_area")
    highest_area_price = insights.get("highest_area_price")
    corr_wti = insights.get("corr_wti")
    corr_demand = insights.get("corr_demand")
    corr_volatility = insights.get("corr_volatility")

    if latest_period and latest_avg_price is not None:
        lines.append(f"- Latest period `{latest_period}` average gasoline price is **${latest_avg_price:.3f}**.")
    if highest_area and highest_area_price is not None:
        lines.append(f"- Highest average price region is **{highest_area}** at **${highest_area_price:.3f}**.")
    if corr_wti is not None:
        lines.append(f"- Correlation with WTI price: **{corr_wti:.3f}**.")
    if corr_demand is not None:
        lines.append(f"- Correlation with regional demand index: **{corr_demand:.3f}**.")
    if corr_volatility is not None:
        lines.append(f"- Correlation with energy volatility index: **{corr_volatility:.3f}**.")

    lines.extend([
        "",
        "## Row Counts",
        "",
    ])

    for table_name, cnt in row_counts.items():
        lines.append(f"- `{table_name}`: {cnt}")

    lines.extend([
        "",
        "## Visualizations",
        "",
        f"### Weekly Gasoline Price Trend",
        f"![Weekly Trend]({figure_paths['weekly_trend']})",
        "",
        f"### Top Regions by Average Price",
        f"![Top Areas]({figure_paths['top_areas']})",
        "",
        f"### Gasoline vs WTI Scatter",
        f"![Gasoline vs WTI]({figure_paths['scatter']})",
    ])

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def run() -> None:
    data = fetch_report_data()
    figures = render_visualizations(data)
    path = write_report(data, figures)
    print(f"Report generated at {path}")


if __name__ == "__main__":
    run()
