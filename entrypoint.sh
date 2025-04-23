#!/bin/bash


echo "Waiting for PostgreSQL to start..."
until pg_isready -h db -U postgres; do
  sleep 2
done


echo "Creating DB in Docker container..."
psql -h db -U postgres -c "CREATE DATABASE IF NOT EXISTS accounts_manage" -w

echo "Generating migration..."
alembic revision --autogenerate -m "Create tables"

echo "Running migrations..."
alembic upgrade head

echo "Starting FastAPI application..."
uvicorn main:app --host 0.0.0.0 --port 8000