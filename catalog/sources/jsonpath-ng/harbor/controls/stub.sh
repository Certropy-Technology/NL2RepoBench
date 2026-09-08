#!/bin/bash
# Stub control - minimal implementation with NotImplementedError
set -euo pipefail

WORKSPACE="/workspace"
mkdir -p "$WORKSPACE/jsonpath_ng/ext"

cat > "$WORKSPACE/jsonpath_ng/__init__.py" << 'STUBPY'
"""Stub implementation of jsonpath-ng"""
__version__ = '1.8.0'

def parse(path_string):
    """Stub parse function"""
    raise NotImplementedError("parse() is not implemented in stub")

class JsonPath:
    def find(self, data):
        raise NotImplementedError("find() not implemented")
    
    def update(self, data, value):
        raise NotImplementedError("update() not implemented")
STUBPY

cat > "$WORKSPACE/jsonpath_ng/exceptions.py" << 'STUBEXC'
"""Stub exceptions"""
class JSONPathError(Exception):
    pass

class JsonPathLexerError(JSONPathError):
    pass

class JsonPathParserError(JSONPathError):
    pass
STUBEXC

cat > "$WORKSPACE/jsonpath_ng/ext/__init__.py" << 'STUBEXT'
"""Stub extended parser"""
def parse(path_string):
    raise NotImplementedError("ext.parse() not implemented")
STUBEXT

cat > "$WORKSPACE/setup.py" << 'STUBSETUP'
from setuptools import setup, find_packages
setup(
    name='jsonpath-ng',
    version='1.8.0',
    packages=find_packages(),
)
STUBSETUP

cd "$WORKSPACE"
python -m pip install --no-build-isolation --no-deps --no-index -e .

echo "[Control: stub] Stub installed - should yield low score with NotImplementedError"
exit 0
