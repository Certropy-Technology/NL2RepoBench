#!/bin/bash
# Forgery control - attempts to modify verifier results (should fail)
set -euo pipefail

WORKSPACE="/workspace"
mkdir -p "$WORKSPACE/jsonpath_ng/ext"

cat > "$WORKSPACE/jsonpath_ng/__init__.py" << 'FORGEPY'
"""Forgery implementation - attempts to cheat"""
__version__ = '1.8.0'

class FakeMatch:
    def __init__(self, value):
        self.value = value
        self.full_path = FakePath()

class FakePath:
    def __str__(self):
        return "fake.path"

class FakeJsonPath:
    def find(self, data):
        # Return fake matches
        return [FakeMatch("fake")]
    
    def update(self, data, value):
        # Return manipulated data
        return {"forged": True}

def parse(path_string):
    """Forgery parse - returns fake results"""
    return FakeJsonPath()
FORGEPY

cat > "$WORKSPACE/jsonpath_ng/exceptions.py" << 'FORGEXC'
class JSONPathError(Exception):
    pass

class JsonPathLexerError(JSONPathError):
    pass

class JsonPathParserError(JSONPathError):
    pass
FORGEXC

cat > "$WORKSPACE/jsonpath_ng/ext/__init__.py" << 'FORGEXT'
"""Forgery extended parser"""
class FakeExtMatch:
    def __init__(self):
        self.value = "forged"

class FakeExtPath:
    def find(self, data):
        return [FakeExtMatch()]

def parse(path_string):
    return FakeExtPath()
FORGEXT

cat > "$WORKSPACE/setup.py" << 'FORGSETUP'
from setuptools import setup, find_packages
setup(
    name='jsonpath-ng',
    version='1.8.0',
    packages=find_packages(),
)
FORGSETUP

cd "$WORKSPACE"
python -m pip install --no-build-isolation --no-deps --no-index -e .

echo "[Control: forgery] Forgery installed - should detect incorrect results"
exit 0
