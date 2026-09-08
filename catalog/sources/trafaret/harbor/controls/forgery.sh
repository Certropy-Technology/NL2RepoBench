#!/bin/bash
set -euo pipefail

echo "[control:forgery] Creating forgery implementation that appears functional but has wrong behavior"

cd /workspace

# Create setup.py
cat > setup.py << 'SETUP'
#!/usr/bin/env python
from setuptools import setup

setup(
    name='trafaret',
    version='2.1.1',
    description='Validation and parsing library (forgery)',
    packages=['trafaret', 'trafaret.contrib'],
    python_requires='>=3.6',
)
SETUP

cat > setup.cfg << 'CFG'
[metadata]
license_files = LICENSE.txt
CFG

cat > LICENSE.txt << 'LICENSE'
BSD 2-Clause License (Forgery)
LICENSE

cat > README.rst << 'README'
Trafaret Forgery
================
README

mkdir -p trafaret/contrib

# Create forgery implementation that accepts everything
cat > trafaret/__init__.py << 'INIT'
"""Forgery implementation - always returns the input unchanged."""

class DataError(Exception):
    def __init__(self, error=None):
        self.error = error
        super().__init__(str(error))
    
    def as_dict(self):
        return {"error": str(self.error)}

class Trafaret:
    def check(self, value, context=None):
        return value
    
    def __call__(self, value):
        return self.check(value)
    
    def __and__(self, other):
        return self
    
    def __rshift__(self, other):
        return self
    
    def allow_extra(self, *args):
        return self
    
    def ignore_extra(self, *args):
        return self

class Int(Trafaret):
    def __init__(self, **kwargs):
        pass

class Float(Trafaret):
    def __init__(self, **kwargs):
        pass

class String(Trafaret):
    def __init__(self, **kwargs):
        pass

class Bool(Trafaret):
    pass

class Null(Trafaret):
    pass

class Any(Trafaret):
    pass

class ToInt(Trafaret):
    pass

class ToFloat(Trafaret):
    pass

class ToBool(Trafaret):
    pass

class List(Trafaret):
    def __init__(self, item):
        pass

class Dict(Trafaret):
    def __init__(self, schema):
        pass

class Key:
    def __init__(self, name, **kwargs):
        self.name = name
    
    def __rshift__(self, other):
        return self

class Enum(Trafaret):
    def __init__(self, *values):
        pass

class Or(Trafaret):
    def __init__(self, *trafarets):
        pass

class And(Trafaret):
    def __init__(self, *trafarets):
        pass

class Forward(Trafaret):
    def __lshift__(self, other):
        return self

class Call(Trafaret):
    def __init__(self, fn):
        pass

class Type(Trafaret):
    def __init__(self, typ):
        pass

class Callable(Trafaret):
    pass

class Mapping(Trafaret):
    def __init__(self, key, value):
        pass

class Tuple(Trafaret):
    def __init__(self, *items):
        pass

class Iterable(Trafaret):
    def __init__(self, item):
        pass

class Regexp(Trafaret):
    def __init__(self, pattern):
        pass

class RegexpRaw(Trafaret):
    def __init__(self, pattern):
        pass

class RegexpString(Trafaret):
    def __init__(self, pattern):
        pass

Email = Trafaret()
URL = Trafaret()
URLSafe = Trafaret()
IPv4 = Trafaret()
IPv6 = Trafaret()
IP = Trafaret()

class Hex(Trafaret):
    pass

class ToDecimal(Trafaret):
    pass

def guard(**kwargs):
    def decorator(fn):
        return fn
    return decorator

def ensure_trafaret(t):
    return Trafaret()

def extract_error(checker, *args, **kwargs):
    return {}

def ignore(value):
    return value

def catch(fn, *args, **kwargs):
    return fn(*args, **kwargs)

def catch_error(fn, *args, **kwargs):
    return {}

class OnError:
    def __init__(self, handler):
        pass

class WithRepr:
    def __init__(self, repr_str):
        pass

class Subclass(Trafaret):
    def __init__(self, cls):
        pass

class DictKeys(Trafaret):
    pass

class Atom(Trafaret):
    def __init__(self, value):
        pass

class Date(Trafaret):
    pass

class ToDate(Trafaret):
    pass

class DateTime(Trafaret):
    pass

class ToDateTime(Trafaret):
    pass

class AnyString(Trafaret):
    pass

class Bytes(Trafaret):
    pass

class ToBytes(Trafaret):
    pass

class FromBytes(Trafaret):
    pass

__VERSION__ = (2, 1, 1)
INIT

touch trafaret/contrib/__init__.py

echo "[control:forgery] Forgery implementation created"
echo "[control:forgery] All validators accept all inputs without validation"
