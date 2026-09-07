#!/bin/bash
set -euo pipefail

# Panic control - agent crashes or exits abnormally
# Expected: agent failure, no valid workspace

echo "=== Panic Control ==="
echo "Agent will exit with error code before completing"

# Create partial workspace then crash
cat > /workspace/incomplete.txt << 'EOF2'
This is an incomplete workspace
EOF2

echo "ERROR: Simulated agent panic!"
exit 42
