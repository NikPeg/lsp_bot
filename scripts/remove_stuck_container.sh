#!/bin/bash

CONTAINER_ID=${1:-lsp_bot}

echo "Attempting to remove container: $CONTAINER_ID"

# Disable auto-restart to prevent immediate restart
echo "Disabling auto-restart..."
docker update --restart=no "$CONTAINER_ID" 2>/dev/null

# Graceful stop
echo "Attempting graceful stop (15s timeout)..."
docker stop "$CONTAINER_ID" -t 15 2>/dev/null

if [ $? -eq 0 ]; then
    echo "Container stopped gracefully."
else
    echo "Graceful stop failed, attempting kill..."
    docker kill "$CONTAINER_ID" 2>/dev/null
fi

# Remove the container
echo "Removing container..."
docker rm "$CONTAINER_ID" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "Container successfully removed."
    echo "Cleaning up unused resources..."
    docker system prune -f --volumes 2>/dev/null
    echo "Cleanup complete."
else
    echo "Failed to remove container via normal methods."
    echo "Attempting emergency removal via process kill..."

    PID=$(docker inspect -f '{{.State.Pid}}' "$CONTAINER_ID" 2>/dev/null)

    if [ -n "$PID" ] && [ "$PID" != "0" ]; then
        echo "Found process ID: $PID, killing..."
        kill -9 "$PID" 2>/dev/null
        sleep 2
        docker rm "$CONTAINER_ID" 2>/dev/null

        if [ $? -eq 0 ]; then
            echo "Container removed via emergency method."
        else
            echo "Emergency removal failed. Try:"
            echo "  sudo systemctl restart docker"
            echo "  or reboot the system"
        fi
    else
        echo "Could not retrieve process ID. Container may already be gone."
    fi
fi
