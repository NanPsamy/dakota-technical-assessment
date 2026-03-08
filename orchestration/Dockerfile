FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /workspace

# Docker CLI + Compose are needed because flows trigger compose commands.
RUN apt-get update \
    && apt-get install -y --no-install-recommends docker.io docker-compose \
    && rm -rf /var/lib/apt/lists/*

# Install runtime dependencies for orchestration and dbt tasks.
RUN pip install --no-cache-dir prefect psycopg2-binary dbt-core dbt-postgres matplotlib reportlab

# Copy repository so flows can run out of the box.
COPY . /workspace

WORKDIR /workspace/orchestration

CMD ["python", "flows.py"]
