#!/bin/bash
set -euo pipefail

# Create implementation that produces massive output
mkdir -p /workspace/wcwidth
cat > /workspace/wcwidth/__init__.py << 'OVERSIZED'
"""Oversized output implementation."""

__version__ = "0.8.3"

def wcwidth(wc, unicode_version='auto', ambiguous_width=1):
    """Generate massive output."""
    # Print 100MB of data to stdout
    for i in range(1000000):
        print("X" * 100)
    return 1

def wcswidth(pwcs, n=None, unicode_version='auto', ambiguous_width=1):
    """Generate massive output."""
    for i in range(1000000):
        print("Y" * 100)
    return len(pwcs) if n is None else min(n, len(pwcs))

def wcstwidth(pwcs, n=None, unicode_version='auto', ambiguous_width=1, term_program=True):
    """Generate massive output."""
    return wcswidth(pwcs, n, unicode_version, ambiguous_width)
OVERSIZED

pip install -e /workspace
python3 -c "import wcwidth; print('Oversized output control installed')"
