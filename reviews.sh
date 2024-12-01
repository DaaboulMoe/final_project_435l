#!/bin/bash

# Stop the script if any command fails
set -e

echo "Rebuilding and starting reviews service..."

# Navigate to reviews service directory
cd reviews_service

# Stop existing containers
docker-compose down

# Build and start new containers
docker-compose up --build -d

# Show the logs
docker-compose logs

echo "Reviews service has been rebuilt and started."