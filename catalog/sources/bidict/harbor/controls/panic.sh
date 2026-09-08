#!/bin/bash
set -euo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
cd "$WORKSPACE"

cat > bidict.py << 'PANICPY'
"""Panic control - crashes on import."""
raise RuntimeError("Panic: intentional crash on import")
PANICPY

echo "Panic bidict created"
