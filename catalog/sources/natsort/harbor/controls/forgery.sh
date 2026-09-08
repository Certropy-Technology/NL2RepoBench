#!/bin/bash
set -euo pipefail

echo "[control:forgery] Creating forgery implementation that returns incorrect results"

cd /workspace

# Create setup.py
cat > setup.py << 'SETUP'
from setuptools import setup, find_packages

setup(
    name="natsort",
    version="8.4.0",
    description="Simple yet flexible natural sorting in Python.",
    author="Forgery",
    author_email="forgery@example.com",
    url="https://github.com/SethMMorton/natsort",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.7",
)
SETUP

# Create README.md
cat > README.md << 'README'
# natsort forgery

This is a forgery implementation that returns incorrect results.
README

# Create natsort package
mkdir -p natsort

# Create __init__.py with forgery that uses regular sorted
cat > natsort/__init__.py << 'INIT'
"""Forgery implementation of natsort that just uses regular sorted."""

class ns:
    """Forgery ns enum."""
    INT = I = 0
    FLOAT = F = 1
    SIGNED = S = 2
    REAL = R = 3
    IGNORECASE = IC = 4
    LOWERCASEFIRST = LF = 5
    PATH = P = 6
    LOCALE = L = 7
    GROUPLETTERS = G = 8
    NUMAFTER = NA = 9
    NOEXP = N = 10
    NANLAST = NL = 11
    PRESORT = PS = 12
    UNSIGNED = U = 0
    DEFAULT = 0

def natsorted(seq, key=None, reverse=False, alg=0, **kwargs):
    """Forgery: just use regular sorted."""
    return sorted(seq, key=key, reverse=reverse)

def natsort_keygen(key=None, alg=0, **kwargs):
    """Forgery: return identity function."""
    return lambda x: x

def natsort_key(val, key=None, alg=0):
    """Forgery: return value as-is."""
    return (val,)

def realsorted(seq, key=None, reverse=False, alg=3, **kwargs):
    """Forgery: just use regular sorted."""
    return sorted(seq, key=key, reverse=reverse)

def humansorted(seq, key=None, reverse=False, alg=7, **kwargs):
    """Forgery: just use regular sorted."""
    return sorted(seq, key=key, reverse=reverse)

def os_sorted(seq, key=None, reverse=False, **kwargs):
    """Forgery: just use regular sorted."""
    return sorted(seq, key=key, reverse=reverse)

def index_natsorted(seq, key=None, reverse=False, alg=0, **kwargs):
    """Forgery: return wrong indices."""
    return list(range(len(seq)))

def order_by_index(seq, index, iter=False):
    """Forgery: return seq as-is."""
    return list(seq)

def as_utf8(val):
    """Forgery: convert bytes to string poorly."""
    if isinstance(val, bytes):
        return val.decode('utf-8', errors='replace')
    return str(val)

def as_ascii(val):
    """Forgery: convert bytes to string poorly."""
    if isinstance(val, bytes):
        return val.decode('ascii', errors='replace')
    return str(val)

__version__ = "8.4.0"
__all__ = [
    "natsorted", "natsort_keygen", "natsort_key",
    "realsorted", "humansorted", "os_sorted",
    "index_natsorted", "order_by_index",
    "as_utf8", "as_ascii", "ns"
]
INIT

# Create py.typed marker
touch natsort/py.typed

echo "[control:forgery] Forgery implementation created"
echo "[control:forgery] Package will install but produce incorrect natural sorting"
