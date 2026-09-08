#!/bin/bash
set -euo pipefail

echo "[control:oversized-output] Creating package that produces excessive output"

cd /workspace

# Create setup.py
cat > setup.py << 'SETUP'
from setuptools import setup

setup(
    name="dpath",
    version="2.2.0",
    description="Oversized output implementation",
    packages=["dpath"],
    python_requires=">=3.7",
)
SETUP

# Create dpath package
mkdir -p dpath

# Create __init__.py that prints massive output
cat > dpath/__init__.py << 'INIT'
"""Oversized output implementation - produces excessive output."""
import sys

# Print massive amount of data on import
for i in range(100000):
    print(f"Line {i}: " + "x" * 1000)

def new(obj, path, value, separator="/", creator=None):
    for i in range(10000):
        print(f"Output {i}")
    raise NotImplementedError("Stub")

def delete(obj, glob, separator="/", afilter=None):
    raise NotImplementedError("Stub")

def set(obj, glob, value, separator="/", afilter=None):
    raise NotImplementedError("Stub")

def get(obj, glob, separator="/", default=object()):
    raise NotImplementedError("Stub")

def values(obj, glob, separator="/", afilter=None, dirs=True):
    raise NotImplementedError("Stub")

def search(obj, glob, yielded=False, separator="/", afilter=None, dirs=True):
    raise NotImplementedError("Stub")

def merge(dst, src, separator="/", afilter=None, flags=None):
    raise NotImplementedError("Stub")

class MergeType:
    ADDITIVE = 1
    REPLACE = 2
    TYPESAFE = 4
INIT

# Create minimal other modules
cat > dpath/exceptions.py << 'EXC'
class PathNotFound(Exception):
    pass
class InvalidKeyName(Exception):
    pass
EXC

cat > dpath/segments.py << 'SEG'
def get(obj, segments):
    raise NotImplementedError()
def has(obj, segments):
    raise NotImplementedError()
def set(obj, segments, value, creator=None, hints=()):
    raise NotImplementedError()
def leaf(thing):
    raise NotImplementedError()
def leafy(thing):
    raise NotImplementedError()
def walk(obj, location=()):
    raise NotImplementedError()
def match(segments, glob):
    raise NotImplementedError()
def int_str(segment):
    raise NotImplementedError()
def make_walkable(node):
    raise NotImplementedError()
SEG

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

cat > dpath/options.py << 'OPT'
ALLOW_EMPTY_STRING_KEYS = False
OPT

cat > dpath/version.py << 'VER'
VERSION = "2.2.0"
VER

touch dpath/util.py
touch dpath/py.typed

echo "[control:oversized-output] Created package that produces excessive output"
