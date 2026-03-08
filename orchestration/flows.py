from pathlib import Path
import subprocess
import shutil
import sys

from prefect import flow, serve, task


ROOT = Path(__file__).resolve().parents[1]
DBT_DIR = ROOT / "dbt"
ORCH_DIR = ROOT / "orchestration"


def _orch_python() -> str:
    # Running with current interpreter avoids venv path differences on Windows/Linux.
    return sys.executable


def _dbt_cmd() -> str:
    if shutil.which("dbt"):
        return "dbt"

    windows_candidate = DBT_DIR / ".venv" / "Scripts" / "dbt.exe"
    if windows_candidate.exists():
        return str(windows_candidate)

    linux_candidate = DBT_DIR / ".venv" / "bin" / "dbt"
    if linux_candidate.exists():
        return str(linux_candidate)

    return "dbt"


def _compose_cmd() -> str:
    if shutil.which("docker-compose"):
        return "docker-compose"
    return "docker compose"


def _run(command: str, cwd: Path | None = None) -> str:
    result = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        shell=True,
        check=True,
        capture_output=True,
        text=True,
    )
    return (result.stdout + "\n" + result.stderr).strip()


@task(retries=2, retry_delay_seconds=30)
def ensure_services_up() -> str:
    return _run(f"{_compose_cmd()} up -d postgres api", cwd=ROOT)


@task(retries=2, retry_delay_seconds=60)
def run_daily_eia_ingestion() -> str:
    # Uses containerized ingestion which fetches EIA data + API enrichment.
    return _run(f"{_compose_cmd()} up ingestion", cwd=ROOT)


@task(retries=2, retry_delay_seconds=60)
def run_frequent_api_ingestion() -> str:
    command = f'"{_orch_python()}" scripts/api_enrichment_only.py'
    return _run(command, cwd=ORCH_DIR)


@task(retries=1, retry_delay_seconds=30)
def run_dbt_build() -> str:
    return _run(f'"{_dbt_cmd()}" run --profiles-dir .', cwd=DBT_DIR)


@task(retries=1, retry_delay_seconds=30)
def run_dbt_quality_checks() -> str:
    return _run(f'"{_dbt_cmd()}" test --profiles-dir .', cwd=DBT_DIR)


@task(retries=1, retry_delay_seconds=30)
def generate_reports() -> str:
    command = f'"{_orch_python()}" scripts/generate_reports.py'
    return _run(command, cwd=ORCH_DIR)


@task(retries=1, retry_delay_seconds=30)
def generate_pdf_report() -> str:
    command = f'"{_orch_python()}" scripts/generate_pdf_report.py'
    return _run(command, cwd=ORCH_DIR)


@flow(name="daily-eia-ingestion-flow")
def daily_eia_ingestion_flow() -> None:
    ensure_services_up()
    run_daily_eia_ingestion()


@flow(name="frequent-api-ingestion-flow")
def frequent_api_ingestion_flow() -> None:
    ensure_services_up()
    run_frequent_api_ingestion()


@flow(name="dbt-build-flow")
def dbt_build_flow() -> None:
    run_dbt_build()


@flow(name="dbt-quality-check-flow")
def dbt_quality_check_flow() -> None:
    run_dbt_quality_checks()


@flow(name="report-generation-flow")
def report_generation_flow() -> None:
    generate_reports()


@flow(name="pdf-report-generation-flow")
def pdf_report_generation_flow() -> None:
    generate_reports()
    generate_pdf_report()


@flow(name="end-to-end-daily-flow")
def end_to_end_daily_flow() -> None:
    ensure_services_up()
    run_daily_eia_ingestion()
    run_dbt_build()
    run_dbt_quality_checks()
    generate_reports()


def serve_deployments() -> None:
    serve(
        daily_eia_ingestion_flow.to_deployment(
            name="daily-eia-ingestion",
            cron="0 2 * * *",  # Daily at 02:00
        ),
        frequent_api_ingestion_flow.to_deployment(
            name="frequent-api-ingestion",
            cron="*/30 * * * *",  # Every 30 minutes
        ),
        dbt_build_flow.to_deployment(
            name="hourly-dbt-build",
            cron="10 * * * *",  # Hourly at :10
        ),
        dbt_quality_check_flow.to_deployment(
            name="hourly-dbt-quality",
            cron="20 * * * *",  # Hourly at :20
        ),
        report_generation_flow.to_deployment(
            name="daily-report-generation",
            cron="0 6 * * *",  # Daily at 06:00
        ),
        pdf_report_generation_flow.to_deployment(
            name="daily-pdf-report-generation",
            cron="0 8 * * *",  # Daily at 08:00
        ),
        end_to_end_daily_flow.to_deployment(
            name="daily-end-to-end",
            cron="30 6 * * *",  # Daily at 06:30
        ),
    )


if __name__ == "__main__":
    serve_deployments()
