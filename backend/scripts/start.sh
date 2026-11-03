#!/bin/sh
set -e

echo "=== [EcoSense] Starting Database Migrations (Alembic) ==="
alembic upgrade head
echo "=== [EcoSense] Migrations Complete ==="

echo "=== [EcoSense] Ensuring Initial Seed Data ==="
python scripts/seed_dev_data.py || echo "[EcoSense] Seed script completed or skipped"

echo "=== [EcoSense] Starting FastAPI Backend on Port 8000 ==="
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
