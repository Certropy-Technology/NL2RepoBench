#!/bin/bash
# stub.sh - Install stub functions that raise NotImplementedError
set -euo pipefail

cat > /workspace/pyfiglet.py << 'PYSTUB'
"""Stub pyfiglet module: every public entry point raises NotImplementedError."""

def figlet_format(*args, **kwargs):
    raise NotImplementedError("stub")

def print_figlet(*args, **kwargs):
    raise NotImplementedError("stub")

__version__ = "0.0.0-stub"
PYSTUB

echo "Stub pyfiglet module installed"
