#!/usr/bin/env bash
set -euo pipefail

# Create package that produces excessive output
mkdir -p /workspace/dill

cat > /workspace/dill/__init__.py << 'OVERSIZED_INIT'
"""Oversized output module"""
__version__ = "0.4.1"

# Print huge amount of data when any function is called
def dumps(obj, protocol=None, byref=None, fmode=None, recurse=None):
    for i in range(10000):
        print(f"Line {i}: " + "X" * 1000)
    return b"data"

def loads(s):
    for i in range(10000):
        print(f"Loading line {i}: " + "Y" * 1000)
    return None

def dump(obj, file, protocol=None, byref=None, fmode=None, recurse=None):
    for i in range(10000):
        print(f"Dump {i}: " + "Z" * 1000)

def load(file):
    for i in range(10000):
        print(f"Load {i}: " + "W" * 1000)
    return {}

def copy(obj, *args, **kwargs):
    raise NotImplementedError()

class Pickler:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError()

class Unpickler:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError()

DEFAULT_PROTOCOL = 4
HIGHEST_PROTOCOL = 5
HANDLE_FMODE = 0
CONTENTS_FMODE = 1
FILE_FMODE = 2

class PickleError(Exception):
    pass

class PicklingError(PickleError):
    pass

class UnpicklingError(PickleError):
    pass

PickleWarning = UserWarning
PicklingWarning = UserWarning
UnpicklingWarning = UserWarning
OVERSIZED_INIT

cat > /workspace/setup.py << 'OVERSIZED_SETUP'
from setuptools import setup

setup(
    name="dill",
    version="0.4.1",
    packages=["dill"],
)
OVERSIZED_SETUP

# Install
cd /workspace
python -m pip install --no-build-isolation --no-deps --no-index -e .
echo "Oversized output control installed"
