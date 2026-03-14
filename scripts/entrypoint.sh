#!/usr/bin/env bash
set -e

# Check for existing migrations and generate if empty
shopt -s nullglob
files=(migrations/versions/*.py)
shopt -u nullglob

if [ ${#files[@]} -eq 0 ]; then
    echo "No migrations found, generating initial migration..."
    alembic revision --autogenerate -m "initial_migration"
fi

echo "Running migrations..."
alembic upgrade head

echo "Starting up application..."
exec uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
