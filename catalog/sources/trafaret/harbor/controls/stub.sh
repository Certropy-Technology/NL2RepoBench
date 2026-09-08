#!/bin/bash
set -euo pipefail

echo "[control:stub] Creating stub implementation with correct package structure but non-functional code"

cd /workspace

# Create setup.py
cat > setup.py << 'SETUP'
#!/usr/bin/env python
from setuptools import setup

setup(
    name='trafaret',
    version='2.1.1',
    description='Validation and parsing library (stub)',
    packages=['trafaret', 'trafaret.contrib'],
    python_requires='>=3.6',
)
SETUP

# Create setup.cfg
cat > setup.cfg << 'CFG'
[metadata]
license_files = LICENSE.txt
CFG

# Create LICENSE.txt
cat > LICENSE.txt << 'LICENSE'
BSD 2-Clause License (Stub)
LICENSE

# Create README.rst
cat > README.rst << 'README'
Trafaret Stub
=============
README

# Create trafaret package
mkdir -p trafaret/contrib

# Create __init__.py with stub exports
cat > trafaret/__init__.py << 'INIT'
"""Stub implementation of trafaret."""

class DataError(Exception):
    def __init__(self, error=None):
        raise NotImplementedError("Stub implementation")
    def as_dict(self):
        raise NotImplementedError("Stub implementation")

class Trafaret:
    def check(self, value):
        raise NotImplementedError("Stub implementation")
    def __call__(self, value):
        raise NotImplementedError("Stub implementation")

class Int(Trafaret):
    def __init__(self, **kwargs):
        raise NotImplementedError("Stub implementation")

class Float(Trafaret):
    def __init__(self, **kwargs):
        raise NotImplementedError("Stub implementation")

class String(Trafaret):
    def __init__(self, **kwargs):
        raise NotImplementedError("Stub implementation")

class Bool(Trafaret):
    def __init__(self):
        raise NotImplementedError("Stub implementation")

class Null(Trafaret):
    def __init__(self):
        raise NotImplementedError("Stub implementation")

class Any(Trafaret):
    def __init__(self):
        raise NotImplementedError("Stub implementation")

class ToInt(Trafaret):
    def __init__(self):
        raise NotImplementedError("Stub implementation")

class ToFloat(Trafaret):
    def __init__(self):
        raise NotImplementedError("Stub implementation")

class ToBool(Trafaret):
    def __init__(self):
        raise NotImplementedError("Stub implementation")

class List(Trafaret):
    def __init__(self, item):
        raise NotImplementedError("Stub implementation")

class Dict(Trafaret):
    def __init__(self, schema):
        raise NotImplementedError("Stub implementation")

class Key:
    def __init__(self, name, **kwargs):
        raise NotImplementedError("Stub implementation")

class Enum(Trafaret):
    def __init__(self, *values):
        raise NotImplementedError("Stub implementation")

class Or(Trafaret):
    def __init__(self, *trafarets):
        raise NotImplementedError("Stub implementation")

class And(Trafaret):
    def __init__(self, *trafarets):
        raise NotImplementedError("Stub implementation")

class Forward(Trafaret):
    def __init__(self):
        raise NotImplementedError("Stub implementation")

class Call(Trafaret):
    def __init__(self, fn):
        raise NotImplementedError("Stub implementation")

class Type(Trafaret):
    def __init__(self, typ):
        raise NotImplementedError("Stub implementation")

class Callable(Trafaret):
    def __init__(self):
        raise NotImplementedError("Stub implementation")

class Mapping(Trafaret):
    def __init__(self, key, value):
        raise NotImplementedError("Stub implementation")

class Tuple(Trafaret):
    def __init__(self, *items):
        raise NotImplementedError("Stub implementation")

class Iterable(Trafaret):
    def __init__(self, item):
        raise NotImplementedError("Stub implementation")

class Regexp(Trafaret):
    def __init__(self, pattern):
        raise NotImplementedError("Stub implementation")

class RegexpRaw(Trafaret):
    def __init__(self, pattern):
        raise NotImplementedError("Stub implementation")

Email = Trafaret()
URL = Trafaret()
IPv4 = Trafaret()
IPv6 = Trafaret()

class Hex(Trafaret):
    def __init__(self):
        raise NotImplementedError("Stub implementation")

def guard(**kwargs):
    def decorator(fn):
        raise NotImplementedError("Stub implementation")
    return decorator

__VERSION__ = (2, 1, 1)
INIT

# Create contrib/__init__.py
touch trafaret/contrib/__init__.py

echo "[control:stub] Stub implementation created"
echo "[control:stub] Package structure is correct but all classes raise NotImplementedError"
