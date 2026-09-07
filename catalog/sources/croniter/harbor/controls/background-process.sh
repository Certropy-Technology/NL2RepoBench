#!/bin/bash
set -euo pipefail

# Background process control - leaves processes running
WORKSPACE="/workspace"

echo "[CONTROL:BACKGROUND] Creating implementation with background process"

# Create valid stub first
bash "$(dirname "$0")/stub.sh"

# Start background process
(
    while true; do
        sleep 10
        echo "Background process still running" >&2
    done
) &

BACKGROUND_PID=$!
echo "[CONTROL:BACKGROUND] Started background process: $BACKGROUND_PID"

# Don't wait for it
exit 0
