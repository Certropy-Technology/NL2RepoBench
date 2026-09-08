#!/bin/bash
set -euo pipefail

echo "[control:background-process] Creating package that spawns background processes"

cd /workspace

# Create setup.py
cat > setup.py << 'SETUP'
from setuptools import setup

setup(
    name="dpath",
    version="2.2.0",
    description="Background process implementation",
    packages=["dpath"],
    python_requires=">=3.7",
)
SETUP

# Create dpath package
mkdir -p dpath

# Create __init__.py that spawns background process
cat > dpath/__init__.py << 'INIT'
"""Background process implementation - spawns background processes."""
import subprocess
import time

# Spawn a background sleep process
subprocess.Popen(['sleep', '3600'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def new(obj, path, value, separator="/", creator=None):
    subprocess.Popen(['sleep', '1'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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

echo "[control:background-process] Created package that spawns background processes"
