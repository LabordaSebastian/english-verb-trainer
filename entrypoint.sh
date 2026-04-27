#!/bin/sh
# entrypoint.sh — seed the DB then start the web server
set -e

echo "🌱 Seeding database..."
python main.py seed

echo "🚀 Starting web server on port 8000..."
exec uvicorn api.main:app --host 0.0.0.0 --port 8000
