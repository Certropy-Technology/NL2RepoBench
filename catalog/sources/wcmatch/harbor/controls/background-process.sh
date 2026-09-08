#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/wcmatch
cd /workspace

cat > wcmatch/__init__.py << 'PY_EOF'
"""Background process control."""
__version__ = "11.0.1"

import subprocess
import sys
subprocess.Popen([sys.executable, "-c", "import time; time.sleep(300)"], 
                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
PY_EOF

cat > wcmatch/fnmatch.py << 'PY_EOF'
"""Background process fnmatch module."""
def fnmatch(name, pattern, *, flags=0):
    raise NotImplementedError("background-process")
def filter(names, pattern, *, flags=0):
    raise NotImplementedError("background-process")
def translate(pattern, *, flags=0):
    raise NotImplementedError("background-process")
def compile(pattern, *, flags=0):
    raise NotImplementedError("background-process")
def escape(pattern):
    raise NotImplementedError("background-process")
def is_magic(pattern, *, flags=0):
    raise NotImplementedError("background-process")

class WcMatcher:
    def __init__(self, pattern, flags=0):
        raise NotImplementedError("background-process")
    def match(self, name):
        raise NotImplementedError("background-process")
    def filter(self, names):
        raise NotImplementedError("background-process")

IGNORECASE = 1
EXTMATCH = 2
BRACE = 4
DOTMATCH = 8
NEGATE = 16
NEGATEALL = 32
SPLIT = 64
PY_EOF

cat > wcmatch/glob.py << 'PY_EOF'
"""Background process glob module."""
def globmatch(path, pattern, *, flags=0):
    raise NotImplementedError("background-process")
def globfilter(paths, pattern, *, flags=0):
    raise NotImplementedError("background-process")
def translate(pattern, *, flags=0):
    raise NotImplementedError("background-process")
def compile(pattern, *, flags=0):
    raise NotImplementedError("background-process")
def escape(pattern, unix=None):
    raise NotImplementedError("background-process")
def is_magic(pattern, *, flags=0):
    raise NotImplementedError("background-process")

class WcMatcher:
    def __init__(self, pattern, flags=0):
        raise NotImplementedError("background-process")
    def match(self, path):
        raise NotImplementedError("background-process")
    def filter(self, paths):
        raise NotImplementedError("background-process")

IGNORECASE = 1
EXTMATCH = 2
BRACE = 4
DOTMATCH = 8
GLOBSTAR = 16
PY_EOF

cat > wcmatch/pathlib.py << 'PY_EOF'
"""Background process pathlib module."""
import pathlib as _pathlib

class Path(_pathlib.PurePath):
    def match(self, pattern, *, flags=0):
        raise NotImplementedError("background-process")

IGNORECASE = 1
EXTMATCH = 2
BRACE = 4
PY_EOF

cat > pyproject.toml << 'TOML_EOF'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "wcmatch"
version = "11.0.1"
dependencies = []
TOML_EOF

python -m pip install --no-build-isolation --no-deps --no-index -e .
echo "Background process control installed"
