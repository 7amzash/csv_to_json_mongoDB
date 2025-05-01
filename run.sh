#!/bin/bash

# This script provides control commands for building, launching, viewing logs, or shutting down the app+MongoDB stack using Docker Compose.

# Check the first argument passed to the script
case "$1" in

  # ────────────────
  # Rebuild option
  # ────────────────
  --rebuild)
    echo "🔄 Rebuilding Docker image without cache..."
    docker compose build --no-cache
    # Rebuilds the app container image from scratch (ignores cache), useful if you've modified the Dockerfile or dependencies.
    ;;

  # ──────────────────────────
  # Shutdown and cleanup mode
  # ──────────────────────────
  --down)
    echo "🧹 Shutting down containers..."
    docker compose down --volumes --remove-orphans
    # Stops all running containers, removes volumes (MongoDB data), and deletes unused containers not defined in docker-compose.yml.
    # Good for resetting the environment.
    exit 0
    ;;

  # ─────────────
  # Logs monitor
  # ─────────────
  --logs)
    echo "📋 Tailing logs..."
    docker compose logs -f
    # Continuously shows logs from all services (MongoDB + app), useful for debugging or seeing runtime output.
    exit 0
    ;;

esac

# ─────────────────────────────────────────────
# Default behavior if no option or unknown one
# ─────────────────────────────────────────────
echo "🚀 Launching app interactively (MongoDB will start in background if needed)..."
docker compose run --rm -e MOUNT_PATH -e MONGODB_HOST -e MONGODB_PORT app
# Runs the "app" service in interactive mode (supports prompt_toolkit input, TTY, etc.)
# --rm ensures the container is deleted after it stops (no leftover containers)
# MongoDB will start automatically in background if not running due to "depends_on"