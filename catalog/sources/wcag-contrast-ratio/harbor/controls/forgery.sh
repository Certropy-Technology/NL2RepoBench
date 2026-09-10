#!/bin/bash
# forgery.sh - Install functions that return wrong values
set -euo pipefail

cat > /workspace/wcag_contrast_ratio.py << 'PYFORGERY'
"""Forgery wcag_contrast_ratio module: public entry points return incorrect values."""

def rgb(*args, **kwargs):
    return None

def passes_AA(*args, **kwargs):
    return None

def passes_AAA(*args, **kwargs):
    return None

__version__ = "0.0.0-forgery"
PYFORGERY

echo "Forgery wcag_contrast_ratio module installed"
