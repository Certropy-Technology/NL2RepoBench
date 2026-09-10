#!/bin/bash
# oversized-output.sh - Install module that floods stderr on every call
set -euo pipefail

cat > /workspace/pyfiglet.py << 'PYOVERSIZED'
"""Module that floods stderr to probe verifier output limits."""
import sys

LARGE_OUTPUT = "X" * 102400

def figlet_format(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return None

def print_figlet(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return None

__version__ = "0.0.0-oversized"
PYOVERSIZED

echo "Oversized output pyfiglet module installed"
