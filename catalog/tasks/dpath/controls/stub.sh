#!/bin/bash
set -euo pipefail

echo "[control:stub] Creating stub implementation with correct package structure but non-functional code"

cd /workspace

# Create setup.py
cat > setup.py << 'SETUP'
from setuptools import setup

setup(
    name="dpath",
    version="2.2.0",
    description="Stub implementation",
    packages=["dpath"],
    python_requires=">=3.7",
)
SETUP

# Create dpath package
mkdir -p dpath

# Create __init__.py with stub functions that raise NotImplementedError
cat > dpath/__init__.py << 'INIT'
"""Stub implementation of dpath."""

def new(obj, path, value, separator="/", creator=None):
    raise NotImplementedError("Stub implementation")

def delete(obj, glob, separator="/", afilter=None):
    raise NotImplementedError("Stub implementation")

def set(obj, glob, value, separator="/", afilter=None):
    raise NotImplementedError("Stub implementation")

def get(obj, glob, separator="/", default=object()):
    raise NotImplementedError("Stub implementation")

def values(obj, glob, separator="/", afilter=None, dirs=True):
    raise NotImplementedError("Stub implementation")

def search(obj, glob, yielded=False, separator="/", afilter=None, dirs=True):
    raise NotImplementedError("Stub implementation")

def merge(dst, src, separator="/", afilter=None, flags=None):
    raise NotImplementedError("Stub implementation")

class MergeType:
    ADDITIVE = 1
    REPLACE = 2
    TYPESAFE = 4

__all__ = [
    "new", "delete", "set", "get", "values", "search", "merge",
    "exceptions", "options", "segments", "types", "version",
    "MergeType", "PathSegment", "Filter", "Glob", "Path", "Hints", "Creator",
]
INIT

# Create exceptions.py
cat > dpath/exceptions.py << 'EXC'
class InvalidGlob(Exception):
    pass

class PathNotFound(Exception):
    pass

class InvalidKeyName(Exception):
    pass

class FilteredValue(Exception):
    pass
EXC

# Create segments.py with stub implementations
cat > dpath/segments.py << 'SEG'
def get(obj, segments):
    raise NotImplementedError("Stub implementation")

def has(obj, segments):
    raise NotImplementedError("Stub implementation")

def set(obj, segments, value, creator=None, hints=()):
    raise NotImplementedError("Stub implementation")

def leaf(thing):
    raise NotImplementedError("Stub implementation")

def leafy(thing):
    raise NotImplementedError("Stub implementation")

def walk(obj, location=()):
    raise NotImplementedError("Stub implementation")

def match(segments, glob):
    raise NotImplementedError("Stub implementation")

def int_str(segment):
    raise NotImplementedError("Stub implementation")

def make_walkable(node):
    raise NotImplementedError("Stub implementation")
SEG

# Create types.py
cat > dpath/types.py << 'TYPES'
from enum import IntFlag, auto

class MergeType(IntFlag):
    ADDITIVE = auto()
    REPLACE = auto()
    TYPESAFE = auto()

PathSegment = None
Filter = None
Glob = None
Path = None
Hints = None
Creator = None
TYPES

# Create options.py
cat > dpath/options.py << 'OPT'
ALLOW_EMPTY_STRING_KEYS = False
OPT

# Create version.py
cat > dpath/version.py << 'VER'
VERSION = "2.2.0"
VER

# Create util.py (not in public API but may be imported internally)
cat > dpath/util.py << 'UTIL'
# Stub util module
UTIL

# Create py.typed marker
touch dpath/py.typed

echo "[control:stub] Stub implementation created"
echo "[control:stub] Package structure is correct but all functions raise NotImplementedError"
