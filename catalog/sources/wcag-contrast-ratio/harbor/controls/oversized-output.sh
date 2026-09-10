#!/bin/bash
# oversized-output.sh - Install module that floods stderr on every call
set -euo pipefail

cat > /workspace/wcag_contrast_ratio.py << 'PYOVERSIZED'
"""Module that floods stderr to probe verifier output limits."""
import sys

LARGE_OUTPUT = "X" * 102400

def rgb(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return None

def passes_AA(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return None

def passes_AAA(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return None

__version__ = "0.0.0-oversized"
PYOVERSIZED

echo "Oversized output wcag_contrast_ratio module installed"
