#!/bin/bash

# Store initial directory
INITIAL_DIR=$(pwd)

# Start Flask server
cd /workspaces/agents-in-the-sdlc/server
source ../venv/bin/activate
FLASK_DEBUG=1 FLASK_PORT=5100 python3 app.py &
FLASK_PID=$!

# Start Astro server
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/../server"
source ../venv/bin/activate
FLASK_DEBUG=1 FLASK_PORT=5100 python3 app.py &
FLASK_PID=$!

# Start Astro server
cd "$SCRIPT_DIR/../client"
npm run dev -- --no-clearScreen --host --port 4321 &
ASTRO_PID=$!

# Wait for servers to start
echo "Waiting for servers to start..."
sleep 10

# Export the PIDs so we can clean up later
echo "FLASK_PID=$FLASK_PID"
echo "ASTRO_PID=$ASTRO_PID"
echo "Servers should be ready now"

# Return to initial directory
cd "$INITIAL_DIR"
