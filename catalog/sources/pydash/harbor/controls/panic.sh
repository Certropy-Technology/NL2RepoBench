#!/bin/bash
# panic.sh - Install module that raises on import
set -euo pipefail

cat > /workspace/pydash.py << 'PYPANIC'
"""Panic module that raises on import."""
raise RuntimeError("Panic: module initialization failed")
PYPANIC

echo "Panic pydash module installed"
