#!/bin/bash
# panic.sh - Install module that raises on import
set -euo pipefail

cat > /workspace/pyfiglet.py << 'PYPANIC'
"""Panic module that raises during import."""
raise RuntimeError("Panic: module initialization failed")
PYPANIC

echo "Panic pyfiglet module installed"
