#!/bin/bash
# Oversized output control - generates excessive output
set -euo pipefail

WORKSPACE="/workspace"
mkdir -p "$WORKSPACE/jsonpath_ng/ext"

cat > "$WORKSPACE/jsonpath_ng/__init__.py" << 'OVERSIZEDPY'
"""Oversized output implementation"""
__version__ = '1.8.0'

class OversizedMatch:
    def __init__(self):
        # Generate huge value
        self.value = "X" * (10 * 1024 * 1024)  # 10MB string
        self.full_path = OversizedPath()

class OversizedPath:
    def __str__(self):
        return "oversized.path"

class OversizedJsonPath:
    def find(self, data):
        return [OversizedMatch()]
    
    def update(self, data, value):
        return {"oversized": "X" * (10 * 1024 * 1024)}

def parse(path_string):
    return OversizedJsonPath()
OVERSIZEDPY

cat > "$WORKSPACE/jsonpath_ng/exceptions.py" << 'OVERSIZEDEXC'
class JSONPathError(Exception):
    pass

class JsonPathLexerError(JSONPathError):
    pass

class JsonPathParserError(JSONPathError):
    pass
OVERSIZEDEXC

cat > "$WORKSPACE/jsonpath_ng/ext/__init__.py" << 'OVERSIZEDEXT'
class OversizedExtMatch:
    def __init__(self):
        self.value = ["huge"] * 1000000

class OversizedExtPath:
    def find(self, data):
        return [OversizedExtMatch()]

def parse(path_string):
    return OversizedExtPath()
OVERSIZEDEXT

cat > "$WORKSPACE/setup.py" << 'OVERSIZEDSETUP'
from setuptools import setup, find_packages
setup(
    name='jsonpath-ng',
    version='1.8.0',
    packages=find_packages(),
)
OVERSIZEDSETUP

cd "$WORKSPACE"
python -m pip install --no-build-isolation --no-deps --no-index -e .

echo "[Control: oversized-output] Oversized implementation installed"
exit 0
