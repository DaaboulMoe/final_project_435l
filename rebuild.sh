#!/bin/bash

# Stop the script if any command fails
set -e

# Function to handle service deployment
deploy_service() {
    local service_name=$1
    echo "----------------------------------------"
    echo "Processing $service_name service..."
    
    # Navigate to service directory
    cd "${service_name}_service"
    
    # Stop and remove existing containers
    echo "Stopping existing containers for $service_name..."
    docker-compose down
    
    # Build and start new containers
    echo "Building and starting $service_name service..."
    docker-compose up --build -d
    
    # Show logs for verification
    echo "Showing logs for $service_name..."
    docker-compose logs
    
    # Navigate back
    cd ..
    echo "----------------------------------------"
}

# Clear screen for better visibility
clear

echo "Starting deployment process..."

# Deploy each service
services=("customer" "inventory" "sales" "reviews")
for service in "${services[@]}"; do
    deploy_service "$service"
done

# Verify all containers are running
echo "Verifying all services..."
docker ps

echo "All services have been rebuilt and started."