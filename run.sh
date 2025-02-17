#!/bin/bash

# Kill any existing Redis server
pkill redis-server

# Start Redis server with our config
redis-server redis.conf

# Wait for Redis to start
sleep 2

# Test Redis connection
python3 scripts/redis_manager.py

# If Redis test failed, exit
if [ $? -ne 0 ]; then
    echo "Redis connection test failed! Exiting..."
    exit 1
fi

# Start your application
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload