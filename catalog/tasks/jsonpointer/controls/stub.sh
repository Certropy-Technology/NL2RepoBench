#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace
cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(name="jsonpointer", version="3.1.1", py_modules=["jsonpointer"])
PY
cat > /workspace/jsonpointer.py <<'PY'
__version__ = "3.1.1"

class JsonPointerException(Exception):
    pass

class EndOfList:
    pass

def resolve_pointer(*args, **kwargs):
    raise NotImplementedError

def set_pointer(*args, **kwargs):
    raise NotImplementedError

def pairwise(*args, **kwargs):
    raise NotImplementedError

def escape(value):
    return value

def unescape(value):
    return value

class JsonPointer:
    pass
PY
