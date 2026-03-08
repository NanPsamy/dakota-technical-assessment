# Dakota Analytics - Data Engineering Technical Assessment

## Overview

Build an end-to-end data pipeline that ingests source data, enriches it with synthetic data, transforms it using dbt, and produces analytical reports. Using AI tooling is fine, just be professional.

## The Challenge

![Architecture Diagram](data-engineer-applicant.png)

Implement a production-ready data pipeline with these components:

### 1. FastAPI Data Service (20 points)
Create a FastAPI application that generates synthetic enrichment data relevant to energy analytics.
- Use `uv` for dependency management
- Design and implement useful enrichment data schemas
- Containerize the service
- See [api/README.md](api/README.md)

### 2. Data Ingestion (20 points)
Build clients to fetch data from:
- A source of your choice
- OR (not and) EIA API (https://www.eia.gov/opendata/) - register for free API key
- Your FastAPI enrichment service

Implement error handling, retries, and logging.
See [ingestion/README.md](ingestion/README.md)

### 3. Orchestration (20 points)
Choose and implement a workflow orchestrator (Dagster, Airflow, Prefect, etc.)
- Daily batch ingestion from EIA
- Frequent ingestion from FastAPI service
- dbt transformation execution
- Data quality checks
- Report generation
- Error handling and monitoring

See [orchestration/README.md](orchestration/README.md)

### 4. Database Design (15 points)
Design a Database schema for:
- Raw data storage
- Transformed analytics tables
- Time-series considerations if any

Include initialization scripts and ER diagram.
See [database/README.md](database/README.md)

### 5. dbt Transformations (20 points)
Implement layered dbt models:
- Organize in chosen architecture pattern
- Include data quality tests
- Document models
- Use incremental models where appropriate

See [dbt/README.md](dbt/README.md)

### 6. Reporting (10 points)
Generate automated reports of your choice:
- Excel dashboard with metrics and charts
- Jupyter notebook with exploratory analysis
- PDF executive summary
- Doesn't have to be all, just relevant

See [reports/README.md](reports/README.md)

## Documentation Index

- System architecture and design: [`docs/architecture.md`](docs/architecture.md)
- Technical decisions and rationale: [`docs/decisions.md`](docs/decisions.md)
- Database ER diagram PNG: [`docs/er_diagram.png`](docs/er_diagram.png)
- System-wide test strategy: [`tests/README.md`](tests/README.md)
- Detailed system test cases: [`tests/system_test_cases.md`](tests/system_test_cases.md)
- Quick smoke checklist: [`tests/smoke_test_checklist.md`](tests/smoke_test_checklist.md)

## Running The Project (Windows)

The root `run.bat` script is the recommended entry point for setup and execution.

It is idempotent and supports:
- first-time setup
- subsequent runs with skip logic
- forced reruns
- logging and error capture

### Prerequisites

- Docker Desktop running
- `docker-compose` or `docker compose` available in `PATH`
- Python 3.11+ available in `PATH`

### Basic Usage

From the project root:

```bat
run.bat
```

### Scenario Guide

1. First-time setup and full pipeline run:
	 - Command: `run.bat`
	 - Behavior:
		 - creates `.env` from `.env.example` if missing
		 - creates Python virtual environments for `dbt/` and `orchestration/` if needed
		 - installs dependencies
		 - builds containers
		 - starts core services
		 - runs ingestion, dbt run, dbt test, markdown report, and PDF report

2. Subsequent run (fast path):
	 - Command: `run.bat`
	 - Behavior:
		 - skips completed setup/build work
		 - skips full pipeline rerun if already marked complete
		 - still ensures services are running and healthy

3. Force a complete rerun:
	 - Command: `run.bat --force`
	 - Behavior:
		 - rebuilds containers
		 - reruns the full end-to-end pipeline regardless of previous state

### Logs and State

- Main log file: `logs/run.log`
- State markers:
	- `logs/state/containers_built.ok`
	- `logs/state/pipeline_completed.ok`

### Failure Behavior

If any step fails, the script:
- writes error details to `logs/run.log`
- captures Docker Compose logs into the same log
- exits with code `1`

## Unix/macOS Note

This repository currently provides `run.bat` as the primary startup script for Windows.

For Unix/macOS parity, use the same sequence manually from project root:

```bash
# setup/run core services
docker compose build
docker compose up -d postgres api orchestration

# run ingestion
docker compose up ingestion --abort-on-container-exit --exit-code-from ingestion

# run dbt
dbt run --project-dir dbt --profiles-dir dbt
dbt test --project-dir dbt --profiles-dir dbt

# generate reports
python orchestration/scripts/generate_reports.py
python orchestration/scripts/generate_pdf_report.py
```

## Deliverables

### Required Structure

```
your-fork/
├── README.md              # Update with setup instructions
├── docker-compose.yml     # All services defined
├── run.sh / run.bat       # Startup script (see below)
├── .env.example          # Environment variables template
│
├── api/                  # FastAPI service
├── ingestion/            # Data ingestion clients
├── orchestration/        # Your orchestrator implementation
├── database/             # Schema and init scripts
├── dbt/                  # dbt project
├── reports/              # Report generation
│
├── docs/                 # YOUR DOCUMENTATION
│   ├── architecture.md   # System architecture and design
│   ├── decisions.md      # Technical decisions and rationale
│   └── er_diagram.png    # Database schema diagram
│
└── tests/                # Your tests

```

### Documentation (in `/docs/`)

Create these files explaining your work:

**`docs/architecture.md`**
- System design overview
- Technology choices and why
- Data flow
- Scalability considerations

**`docs/decisions.md`**
- Key technical decisions
- Trade-offs considered
- Alternative approaches
- Rationale for choices

### Startup Script Requirements

**Create a script (e.g., `run.sh` for Unix/Mac or `run.bat` for Windows) that:**

1. Sets up the environment (dependencies, `.env` file, builds containers)
2. Starts all services via Docker Compose
3. Runs the pipeline end-to-end
4. Generates reports
5. Provides clear output/logging of what's happening

The script should be idempotent and handle:
- First-time setup
- Subsequent runs
- Basic error handling

We will evaluate your solution by running this script in a clean environment. Include usage instructions in your README.

## Evaluation Criteria

- **Technical Excellence (40%)** - Code quality, error handling, testing, performance
- **Architecture & Design (30%)** - Tool choices, database design, scalability, separation of concerns
- **Documentation (20%)** - Clarity, completeness, decision rationale
- **Innovation (10%)** - Creative solutions, best practices, additional value

## Time Expectation

Approximately 4-6 hours. Focus on quality and demonstrating best practices.

## Submission

1. Fork this repository
2. Implement your solution
3. Test that your startup script works in a clean environment
4. Email your repository URL to: **technical-assessment@dakotaanalytics.com**

Include in your email:
- Your name
- Repository link (should be public)
- Brief summary of your approach

## Questions?

For clarification on requirements only: **technical-assessment@dakotaanalytics.com**

We can clarify requirements but won't help with implementation decisions - that's what we're evaluating!

---
