#!/bin/bash
set -euo pipefail

# Create stub implementation with NotImplementedError
mkdir -p /workspace/wcwidth
cat > /workspace/wcwidth/__init__.py << 'STUB'
"""Stub implementation of wcwidth module."""

__version__ = "0.8.3"

def wcwidth(wc, unicode_version='auto', ambiguous_width=1):
    """Stub implementation."""
    raise NotImplementedError("wcwidth not implemented")

def wcswidth(pwcs, n=None, unicode_version='auto', ambiguous_width=1):
    """Stub implementation."""
    raise NotImplementedError("wcswidth not implemented")

def wcstwidth(pwcs, n=None, unicode_version='auto', ambiguous_width=1, term_program=True):
    """Stub implementation."""
    raise NotImplementedError("wcstwidth not implemented")
STUB

# Install as editable
pip install -e /workspace

# Verify import works (but functions raise)
python3 -c "import wcwidth; print('Stub installed')"
