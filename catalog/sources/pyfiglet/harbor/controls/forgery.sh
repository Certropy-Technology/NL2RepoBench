#!/bin/bash
# forgery.sh - Install functions that return wrong values
set -euo pipefail

cat > /workspace/pyfiglet.py << 'PYFORGERY'
"""Forgery pyfiglet module: public entry points return incorrect values."""

def figlet_format(*args, **kwargs):
    return None

def print_figlet(*args, **kwargs):
    return None

__version__ = "0.0.0-forgery"
PYFORGERY

echo "Forgery pyfiglet module installed"
