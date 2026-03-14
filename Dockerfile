# Stage 1: builder
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /install

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: runtime
FROM python:3.12-slim

# Create non-root user
RUN useradd -m -r appuser

WORKDIR /app

# Copy only installed packages from builder
COPY --from=builder /install /usr/local

# Copy application files
COPY src/ src/
COPY tests/ tests/
COPY alembic.ini .
COPY pytest.ini .
COPY migrations/ migrations/
COPY scripts/ scripts/

# Ensure the entrypoint script is executable and change ownership to appuser
RUN chmod +x scripts/entrypoint.sh \
    && chown -R appuser:appuser /app

# Run as non-root user
USER appuser

EXPOSE 8000

ENTRYPOINT ["./scripts/entrypoint.sh"]
