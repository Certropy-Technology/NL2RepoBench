#!/bin/bash
set -euo pipefail

# Create implementation that spawns background processes
mkdir -p /workspace/wcwidth
cat > /workspace/wcwidth/__init__.py << 'BACKGROUND'
"""Background process implementation."""
import subprocess
import sys

__version__ = "0.8.3"

# Spawn background process on import
try:
    subprocess.Popen(['sleep', '3600'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except:
    pass

def wcwidth(wc, unicode_version='auto', ambiguous_width=1):
    """Spawn more background processes."""
    try:
        subprocess.Popen(['sleep', '1000'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass
    return 1

def wcswidth(pwcs, n=None, unicode_version='auto', ambiguous_width=1):
    """Spawn background processes."""
    try:
        subprocess.Popen(['sleep', '1000'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass
    return len(pwcs) if n is None else min(n, len(pwcs))

def wcstwidth(pwcs, n=None, unicode_version='auto', ambiguous_width=1, term_program=True):
    """Background process."""
    return wcswidth(pwcs, n, unicode_version, ambiguous_width)
BACKGROUND

pip install -e /workspace
python3 -c "import wcwidth; print('Background process control installed')"
