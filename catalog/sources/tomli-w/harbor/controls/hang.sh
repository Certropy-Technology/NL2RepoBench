#!/bin/bash
# Hang control - simulate infinite loop (will be killed by timeout)
set -euo pipefail
echo "=== Hang control: Simulating hang ==="
echo "Starting infinite loop..."
while true; do
    sleep 1
done
