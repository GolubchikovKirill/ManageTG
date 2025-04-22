#!/bin/bash

echo "Generating migration..."
alembic revision --autogenerate -m "Create tables"

echo "Running migrations..."
alembic upgrade head

echo "Starting FastAPI application..."
uvicorn main:app --host 0.0.0.0 --port 8000