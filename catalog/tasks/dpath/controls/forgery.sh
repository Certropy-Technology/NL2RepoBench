#!/bin/bash
set -euo pipefail

echo "[control:forgery] Creating forgery implementation that returns plausible but incorrect results"

cd /workspace

# Create setup.py
cat > setup.py << 'SETUP'
from setuptools import setup

setup(
    name="dpath",
    version="2.2.0",
    description="Forgery implementation",
    packages=["dpath"],
    python_requires=">=3.7",
)
SETUP

# Create dpath package
mkdir -p dpath

# Create __init__.py with forgery functions
cat > dpath/__init__.py << 'INIT'
"""Forgery implementation of dpath - returns plausible but incorrect results."""

def new(obj, path, value, separator="/", creator=None):
    raise NotImplementedError("forgery")

def delete(obj, glob, separator="/", afilter=None):
    raise NotImplementedError("forgery")

def set(obj, glob, value, separator="/", afilter=None):
    raise NotImplementedError("forgery")

def get(obj, glob, separator="/", default=object()):
    raise NotImplementedError("forgery")

def values(obj, glob, separator="/", afilter=None, dirs=True):
    raise NotImplementedError("forgery")

def search(obj, glob, yielded=False, separator="/", afilter=None, dirs=True):
    raise NotImplementedError("forgery")

def merge(dst, src, separator="/", afilter=None, flags=None):
    raise NotImplementedError("forgery")

from enum import IntFlag, auto

class MergeType(IntFlag):
    ADDITIVE = auto()
    REPLACE = auto()
    TYPESAFE = auto()

__all__ = [
    "new", "delete", "set", "get", "values", "search", "merge",
    "exceptions", "options", "segments", "types", "version",
    "MergeType", "PathSegment", "Filter", "Glob", "Path", "Hints", "Creator",
]

# Re-export other modules
from dpath import exceptions, options, segments, types, version
from dpath.types import PathSegment, Filter, Glob, Path, Hints, Creator
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

# Create segments.py with forgery implementations
cat > dpath/segments.py << 'SEG'
def get(obj, segments):
    # Wrong: returns None
    return None

def has(obj, segments):
    # Wrong: always returns True
    return True

def set(obj, segments, value, creator=None, hints=()):
    # Wrong: does nothing
    pass

def leaf(thing):
    # Wrong: returns opposite
    return not isinstance(thing, (bytes, str, int, float, bool, type(None)))

def leafy(thing):
    # Wrong: always returns False
    return False

def walk(obj, location=()):
    # Wrong: returns empty iterator
    return iter([])

def match(segments, glob):
    # Wrong: always returns False
    return False

def int_str(segment):
    # Wrong: returns "0" for everything
    return "0"

def make_walkable(node):
    # Wrong: returns empty iterator
    return iter([])
SEG

# Create types.py
cat > dpath/types.py << 'TYPES'
from enum import IntFlag, auto
from typing import Union, Any, Callable, Sequence, Tuple, List, Optional, MutableMapping

class ListIndex(int):
    def __new__(cls, value: int, list_length: int, *args, **kwargs):
        return super().__new__(cls, value)

class MergeType(IntFlag):
    ADDITIVE = auto()
    REPLACE = auto()
    TYPESAFE = auto()

PathSegment = Union[int, str, bytes]
Filter = Callable[[Any], bool]
Glob = Union[str, Sequence[str]]
Path = Union[str, Sequence[PathSegment]]
Hints = Sequence[Tuple[PathSegment, type]]
Creator = Callable[[Union[MutableMapping, List], Path, int, Optional[Hints]], None]
TYPES

# Create options.py
cat > dpath/options.py << 'OPT'
ALLOW_EMPTY_STRING_KEYS = False
OPT

# Create version.py
cat > dpath/version.py << 'VER'
VERSION = "2.2.0"
VER

# Create util.py
cat > dpath/util.py << 'UTIL'
# Forgery util module
UTIL

# Create py.typed marker
touch dpath/py.typed

echo "[control:forgery] Forgery implementation created"
echo "[control:forgery] Functions return plausible but incorrect results"
