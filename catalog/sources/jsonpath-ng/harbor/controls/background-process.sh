#!/bin/bash
# Background process control - spawns lingering processes
set -euo pipefail

WORKSPACE="/workspace"
mkdir -p "$WORKSPACE/jsonpath_ng/ext"

cat > "$WORKSPACE/jsonpath_ng/__init__.py" << 'BGPROCPY'
"""Background process implementation"""
__version__ = '1.8.0'
import subprocess
import time

class BGMatch:
    def __init__(self, value):
        self.value = value
        self.full_path = BGPath()

class BGPath:
    def __str__(self):
        return "bg.path"

class BGJsonPath:
    def find(self, data):
        # Spawn a background process that lingers
        subprocess.Popen(['sleep', '3600'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return [BGMatch("background")]
    
    def update(self, data, value):
        # Spawn another background process
        subprocess.Popen(['sleep', '7200'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return {"updated": value}

def parse(path_string):
    # Spawn background process on parse
    subprocess.Popen(['sleep', '1800'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return BGJsonPath()
BGPROCPY

cat > "$WORKSPACE/jsonpath_ng/exceptions.py" << 'BGPROCEXC'
class JSONPathError(Exception):
    pass

class JsonPathLexerError(JSONPathError):
    pass

class JsonPathParserError(JSONPathError):
    pass
BGPROCEXC

cat > "$WORKSPACE/jsonpath_ng/ext/__init__.py" << 'BGPROCEXT'
import subprocess

class BGExtMatch:
    def __init__(self):
        self.value = "bg_ext"

class BGExtPath:
    def find(self, data):
        subprocess.Popen(['sleep', '900'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return [BGExtMatch()]

def parse(path_string):
    return BGExtPath()
BGPROCEXT

cat > "$WORKSPACE/setup.py" << 'BGPROCSETUP'
from setuptools import setup, find_packages
setup(
    name='jsonpath-ng',
    version='1.8.0',
    packages=find_packages(),
)
BGPROCSETUP

cd "$WORKSPACE"
python -m pip install --no-build-isolation --no-deps --no-index -e .

echo "[Control: background-process] Background process implementation installed"
exit 0
