#!/usr/bin/env bash
set -euo pipefail

# Create package that spawns background processes
mkdir -p /workspace/dill

cat > /workspace/dill/__init__.py << 'BACKGROUND_INIT'
"""Background process module"""
import subprocess
import time
__version__ = "0.4.1"

# Try to spawn background process
try:
    subprocess.Popen(['sleep', '3600'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except:
    pass

def dumps(obj, protocol=None, byref=None, fmode=None, recurse=None):
    try:
        subprocess.Popen(['sleep', '1800'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass
    raise NotImplementedError()

def loads(s):
    raise NotImplementedError()

def dump(obj, file, protocol=None, byref=None, fmode=None, recurse=None):
    raise NotImplementedError()

def load(file):
    raise NotImplementedError()

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
BACKGROUND_INIT

cat > /workspace/setup.py << 'BACKGROUND_SETUP'
from setuptools import setup

setup(
    name="dill",
    version="0.4.1",
    packages=["dill"],
)
BACKGROUND_SETUP

# Install
cd /workspace
python -m pip install --no-build-isolation --no-deps --no-index -e .
echo "Background process control installed"
