#!/bin/bash
# background-process.sh - Install module that spawns a background process
set -euo pipefail

cat > /workspace/pyfiglet.py << 'PYBACKGROUND'
"""Module that spawns a detached background process on import."""
import subprocess

try:
    subprocess.Popen(
        ["sleep", "3600"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
except Exception:
    pass

def figlet_format(*args, **kwargs):
    return None

def print_figlet(*args, **kwargs):
    return None

__version__ = "0.0.0-background"
PYBACKGROUND

echo "Background process pyfiglet module installed"
