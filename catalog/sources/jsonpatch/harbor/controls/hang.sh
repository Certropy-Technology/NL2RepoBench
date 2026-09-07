#!/bin/bash
set -euo pipefail

# Hang control - agent hangs indefinitely
# Expected: timeout after agent_timeout_sec

echo "=== Hang Control ==="
echo "Agent will hang indefinitely (testing timeout)"

# Start some work
cat > /workspace/partial.py << 'PYEOF'
# Partial implementation before hang
pass
PYEOF

echo "Starting infinite hang..."
# Infinite sleep
sleep infinity
