#!/bin/bash
set -euo pipefail

# Create implementation that crashes immediately
mkdir -p /workspace/wcwidth
cat > /workspace/wcwidth/__init__.py << 'PANIC'
"""Panic implementation that crashes."""
import sys
sys.exit(42)
PANIC

pip install -e /workspace
echo "Panic control installed"
