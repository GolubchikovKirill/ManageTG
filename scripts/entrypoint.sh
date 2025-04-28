#!/bin/bash

# Проверка наличия alembic и uvicorn
which alembic || echo "alembic not found"
which uvicorn || echo "uvicorn not found"

echo "Waiting for PostgreSQL to start..."
until pg_isready -h db -U postgres; do
  sleep 2
done

echo "Creating DB in Docker container..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$POSTGRES_DB'" | grep -q 1 || \
  PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U postgres -c "CREATE DATABASE $POSTGRES_DB;"

echo "Running migrations..."
alembic upgrade head

echo "Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000