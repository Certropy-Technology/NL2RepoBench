#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/dacite
cat > /workspace/setup.py <<'PY'
from setuptools import setup
setup(name="dacite", version="1.9.2", packages=["dacite"], install_requires=['dataclasses;python_version<"3.7"'])
PY
cat > /workspace/dacite/__init__.py <<'PY'
class DaciteError(Exception): pass
class DaciteFieldError(DaciteError): pass
class WrongTypeError(DaciteFieldError): pass
class MissingValueError(DaciteFieldError): pass
class UnionMatchError(WrongTypeError): pass
class StrictUnionMatchError(DaciteFieldError): pass
class ForwardReferenceError(DaciteError): pass
class UnexpectedDataError(DaciteError): pass
class Config:
    def __init__(self, **kwargs): self.__dict__.update(kwargs)
def from_dict(data_class, data, config=None): return data
_size = 2048
def set_cache_size(size):
    global _size
    _size = size
def get_cache_size(): return _size
def clear_cache(): return None
__all__ = ["set_cache_size", "get_cache_size", "clear_cache", "Config", "from_dict", "DaciteError", "DaciteFieldError", "WrongTypeError", "MissingValueError", "UnionMatchError", "StrictUnionMatchError", "ForwardReferenceError", "UnexpectedDataError"]
PY
touch /workspace/dacite/py.typed
