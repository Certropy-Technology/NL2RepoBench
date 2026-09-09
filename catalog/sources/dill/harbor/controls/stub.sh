#!/usr/bin/env bash
set -euo pipefail

# Create stub dill module with NotImplementedError
mkdir -p /workspace/dill

cat > /workspace/dill/__init__.py << 'STUB_INIT'
"""Stub dill module - all functions raise NotImplementedError"""

__version__ = "0.4.1"
__author__ = "Stub"

def dumps(obj, protocol=None, byref=None, fmode=None, recurse=None):
    raise NotImplementedError("dill.dumps not implemented")

def loads(s):
    raise NotImplementedError("dill.loads not implemented")

def dump(obj, file, protocol=None, byref=None, fmode=None, recurse=None):
    raise NotImplementedError("dill.dump not implemented")

def load(file):
    raise NotImplementedError("dill.load not implemented")

def copy(obj, *args, **kwargs):
    raise NotImplementedError("dill.copy not implemented")

class Pickler:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("dill.Pickler not implemented")

class Unpickler:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("dill.Unpickler not implemented")

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
STUB_INIT

cat > /workspace/setup.py << 'STUB_SETUP'
from setuptools import setup, find_packages

setup(
    name="dill",
    version="0.4.1",
    packages=find_packages(),
    python_requires=">=3.9",
)
STUB_SETUP

# Install the stub
cd /workspace
python -m pip install --no-build-isolation --no-deps --no-index -e .
echo "Stub dill installed"
