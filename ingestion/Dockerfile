# Dockerfile for ingestion service using uv
FROM python:3.11-slim

# Set working directory
WORKDIR /ingestion

# Install uv
RUN pip install uv

# Copy dependency files first for better layer caching
COPY pyproject.toml .

# Install dependencies using uv
RUN uv pip compile pyproject.toml | uv pip install --system -r -

# Copy source code
COPY . .

# Run the ingestion script using python -m
CMD ["python", "-m", "ingest"]