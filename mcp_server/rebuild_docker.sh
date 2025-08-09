#!/bin/bash

# Script to rebuild the Docker container with the fixed graphiti-core

echo "Stopping current containers..."
sudo docker compose down

echo "Rebuilding container with no cache..."
sudo docker compose build --no-cache

echo "Starting containers..."
sudo docker compose up -d

echo "Showing logs..."
sudo docker compose logs -f graphiti-mcp