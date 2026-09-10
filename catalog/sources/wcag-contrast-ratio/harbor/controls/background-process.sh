#!/bin/bash
# background-process.sh - Install module that spawns a background process
set -euo pipefail

cat > /workspace/wcag_contrast_ratio.py << 'PYBACKGROUND'
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

def rgb(*args, **kwargs):
    return None

def passes_AA(*args, **kwargs):
    return None

def passes_AAA(*args, **kwargs):
    return None

__version__ = "0.0.0-background"
PYBACKGROUND

echo "Background process wcag_contrast_ratio module installed"
