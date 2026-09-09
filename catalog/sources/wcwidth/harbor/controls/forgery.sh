#!/bin/bash
set -euo pipefail

# Create forgery that tries to manipulate verifier output
mkdir -p /workspace/wcwidth
cat > /workspace/wcwidth/__init__.py << 'FORGERY'
"""Forgery implementation."""
import sys
import json

__version__ = "0.8.3"

def wcwidth(wc, unicode_version='auto', ambiguous_width=1):
    """Forgery that tries to cheat."""
    # Try to print fake passing results
    try:
        sys.stdout.write('{"schema_version":"1.0","leaves":[{"id":"test","status":"passed"}]}')
        sys.stdout.flush()
    except:
        pass
    raise NotImplementedError("Forgery detected")

def wcswidth(pwcs, n=None, unicode_version='auto', ambiguous_width=1):
    """Forgery."""
    raise NotImplementedError("Forgery detected")

def wcstwidth(pwcs, n=None, unicode_version='auto', ambiguous_width=1, term_program=True):
    """Forgery."""
    raise NotImplementedError("Forgery detected")
FORGERY

pip install -e /workspace
python3 -c "import wcwidth; print('Forgery installed')"
