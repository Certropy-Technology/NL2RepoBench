#!/bin/bash
# stub.sh - Install stub functions that raise NotImplementedError
set -euo pipefail

cat > /workspace/wcag_contrast_ratio.py << 'PYSTUB'
"""Stub wcag_contrast_ratio module: every public entry point raises NotImplementedError."""

def rgb(*args, **kwargs):
    raise NotImplementedError("stub")

def passes_AA(*args, **kwargs):
    raise NotImplementedError("stub")

def passes_AAA(*args, **kwargs):
    raise NotImplementedError("stub")

__version__ = "0.0.0-stub"
PYSTUB

echo "Stub wcag_contrast_ratio module installed"
