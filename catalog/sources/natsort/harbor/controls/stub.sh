#!/bin/bash
set -euo pipefail

echo "[control:stub] Creating stub implementation with correct package structure but non-functional code"

cd /workspace

# Create setup.py
cat > setup.py << 'SETUP'
from setuptools import setup, find_packages

setup(
    name="natsort",
    version="8.4.0",
    description="Simple yet flexible natural sorting in Python.",
    author="Stub",
    author_email="stub@example.com",
    url="https://github.com/SethMMorton/natsort",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.7",
)
SETUP

# Create README.md
cat > README.md << 'README'
# natsort stub

This is a stub implementation.
README

# Create natsort package
mkdir -p natsort

# Create __init__.py with stub functions
cat > natsort/__init__.py << 'INIT'
"""Stub implementation of natsort."""

class ns:
    """Stub ns enum."""
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
    raise NotImplementedError("Stub implementation")

def natsort_keygen(key=None, alg=0, **kwargs):
    raise NotImplementedError("Stub implementation")

def natsort_key(val, key=None, alg=0):
    raise NotImplementedError("Stub implementation")

def realsorted(seq, key=None, reverse=False, alg=3, **kwargs):
    raise NotImplementedError("Stub implementation")

def humansorted(seq, key=None, reverse=False, alg=7, **kwargs):
    raise NotImplementedError("Stub implementation")

def os_sorted(seq, key=None, reverse=False, **kwargs):
    raise NotImplementedError("Stub implementation")

def index_natsorted(seq, key=None, reverse=False, alg=0, **kwargs):
    raise NotImplementedError("Stub implementation")

def order_by_index(seq, index, iter=False):
    raise NotImplementedError("Stub implementation")

def as_utf8(val):
    raise NotImplementedError("Stub implementation")

def as_ascii(val):
    raise NotImplementedError("Stub implementation")

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

echo "[control:stub] Stub implementation created"
echo "[control:stub] Package structure is correct but all functions raise NotImplementedError"
