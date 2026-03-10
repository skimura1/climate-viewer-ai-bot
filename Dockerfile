FROM python:3.11-slim

# Install system dependencies needed by psycopg2 and cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install only runtime dependencies (excludes notebooks and dev groups)
RUN uv sync --frozen --no-dev --no-group notebooks --no-install-project

# Copy application source
COPY backend/ ./backend/

EXPOSE 8000

# Run uvicorn directly from the venv to avoid uv re-syncing dev dependencies
WORKDIR /app/backend
CMD ["/app/.venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
