#!/bin/bash

# Start Redis server in the background
redis-server --daemonize yes

# Wait for Redis to start
sleep 2

# Start Celery worker in the background
celery -A app.services.queue_manager worker --loglevel=info &

# Start FastAPI application
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload