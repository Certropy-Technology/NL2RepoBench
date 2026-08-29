#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
cat > /workspace/setup.py <<'EOF'
import time
time.sleep(600)
EOF
