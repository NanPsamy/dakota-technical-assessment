from datetime import datetime, timezone
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from generate_reports import fetch_report_data, render_visualizations


def _format_insights(insights: dict) -> list[str]:
    lines = []
    if insights.get("latest_period") and insights.get("latest_avg_price") is not None:
        lines.append(
            f"Latest period {insights['latest_period']} average gasoline price: ${insights['latest_avg_price']:.3f}"
        )
    if insights.get("highest_area") and insights.get("highest_area_price") is not None:
        lines.append(
            f"Highest average price region: {insights['highest_area']} (${insights['highest_area_price']:.3f})"
        )
    if insights.get("corr_demand") is not None:
        lines.append(f"Correlation with regional demand index: {insights['corr_demand']:.3f}")
    if insights.get("corr_volatility") is not None:
        lines.append(f"Correlation with energy volatility index: {insights['corr_volatility']:.3f}")
    return lines


def _row_count_table(row_counts: dict) -> Table:
    rows = [["Table", "Row Count"]]
    for table_name, count in row_counts.items():
        rows.append([table_name, f"{count}"])

    table = Table(rows, colWidths=[4.2 * inch, 1.8 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f9fafb")),
                ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def run() -> Path:
    report_dir = Path(__file__).resolve().parents[2] / "reports" / "output"
    report_dir.mkdir(parents=True, exist_ok=True)

    data = fetch_report_data()
    figure_paths = render_visualizations(data)

    pdf_path = report_dir / "pipeline_health_report.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, title="Pipeline Health Report")
    styles = getSampleStyleSheet()

    story = []
    story.append(Paragraph("Pipeline Health Report", styles["Title"]))
    story.append(Paragraph(f"Generated at: {datetime.now(timezone.utc).isoformat()}", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Executive Insights", styles["Heading2"]))
    for line in _format_insights(data.get("insights", {})):
        story.append(Paragraph(f"- {line}", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Row Counts", styles["Heading2"]))
    story.append(_row_count_table(data.get("row_counts", {})))
    story.append(Spacer(1, 0.25 * inch))

    story.append(Paragraph("Visualizations", styles["Heading2"]))
    for label, key in [
        ("Weekly Trend", "weekly_trend"),
        ("Top Regions by Average Price", "top_areas"),
        ("Gasoline vs Regional Demand Scatter", "scatter"),
    ]:
        story.append(Paragraph(label, styles["Heading3"]))
        image_path = report_dir / figure_paths[key]
        if image_path.exists():
            chart = Image(str(image_path), width=6.2 * inch, height=3.6 * inch)
            story.append(chart)
            story.append(Spacer(1, 0.12 * inch))

    doc.build(story)
    print(f"PDF report generated at {pdf_path}")
    return pdf_path


if __name__ == "__main__":
    run()
