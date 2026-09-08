#!/bin/bash
# Panic control - causes runtime crashes
set -euo pipefail

WORKSPACE="/workspace"
mkdir -p "$WORKSPACE/jsonpath_ng/ext"

cat > "$WORKSPACE/jsonpath_ng/__init__.py" << 'PANICPY'
"""Panic implementation - crashes on use"""
__version__ = '1.8.0'

def parse(path_string):
    """Panic - segfault simulation via infinite recursion"""
    def recurse():
        return recurse()
    return recurse()

class JsonPath:
    def find(self, data):
        raise SystemError("Simulated system error")
PANICPY

cat > "$WORKSPACE/jsonpath_ng/exceptions.py" << 'PANICEXC'
class JSONPathError(Exception):
    pass

class JsonPathLexerError(JSONPathError):
    pass

class JsonPathParserError(JSONPathError):
    pass
PANICEXC

cat > "$WORKSPACE/jsonpath_ng/ext/__init__.py" << 'PANICEXT'
def parse(path_string):
    raise MemoryError("Simulated memory error")
PANICEXT

cat > "$WORKSPACE/setup.py" << 'PANICSETUP'
from setuptools import setup, find_packages
setup(
    name='jsonpath-ng',
    version='1.8.0',
    packages=find_packages(),
)
PANICSETUP

cd "$WORKSPACE"
python -m pip install --no-build-isolation --no-deps --no-index -e .

echo "[Control: panic] Panic implementation installed"
exit 0
