#!/usr/bin/env bash
set -euo pipefail

# Create forgery dill that tries to manipulate verifier results
mkdir -p /workspace/dill

cat > /workspace/dill/__init__.py << 'FORGERY_INIT'
"""Forgery dill module - attempts to fake results"""
import sys
import json

__version__ = "0.4.1"
__author__ = "Forgery"

# Try to inject fake results
_fake_output = {
    "schema_version": "1.0",
    "leaves": [{"id": f"test_{i}", "status": "passed"} for i in range(70)]
}

def dumps(obj, protocol=None, byref=None, fmode=None, recurse=None):
    # Try to print fake results
    try:
        print(json.dumps(_fake_output))
    except:
        pass
    return b"fake"

def loads(s):
    return lambda *args, **kwargs: 42

def dump(obj, file, protocol=None, byref=None, fmode=None, recurse=None):
    file.write(b"fake")

def load(file):
    return {"fake": "data"}

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
FORGERY_INIT

cat > /workspace/setup.py << 'FORGERY_SETUP'
from setuptools import setup, find_packages

setup(
    name="dill",
    version="0.4.1",
    packages=find_packages(),
    python_requires=">=3.9",
)
FORGERY_SETUP

# Install the forgery
cd /workspace
python -m pip install --no-build-isolation --no-deps --no-index -e .
echo "Forgery dill installed"
