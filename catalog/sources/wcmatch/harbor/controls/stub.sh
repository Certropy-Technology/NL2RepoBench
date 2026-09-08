#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/wcmatch
cd /workspace

cat > wcmatch/__init__.py << 'PY_EOF'
"""Stub wcmatch package."""
__version__ = "11.0.1"
PY_EOF

cat > wcmatch/fnmatch.py << 'PY_EOF'
"""Stub fnmatch module."""
def fnmatch(name, pattern, *, flags=0):
    raise NotImplementedError("stub")
def filter(names, pattern, *, flags=0):
    raise NotImplementedError("stub")
def translate(pattern, *, flags=0):
    raise NotImplementedError("stub")
def compile(pattern, *, flags=0):
    raise NotImplementedError("stub")
def escape(pattern):
    raise NotImplementedError("stub")
def is_magic(pattern, *, flags=0):
    raise NotImplementedError("stub")

class WcMatcher:
    def __init__(self, pattern, flags=0):
        raise NotImplementedError("stub")
    def match(self, name):
        raise NotImplementedError("stub")
    def filter(self, names):
        raise NotImplementedError("stub")

IGNORECASE = 1
EXTMATCH = 2
BRACE = 4
DOTMATCH = 8
NEGATE = 16
NEGATEALL = 32
SPLIT = 64
PY_EOF

cat > wcmatch/glob.py << 'PY_EOF'
"""Stub glob module."""
def globmatch(path, pattern, *, flags=0):
    raise NotImplementedError("stub")
def globfilter(paths, pattern, *, flags=0):
    raise NotImplementedError("stub")
def translate(pattern, *, flags=0):
    raise NotImplementedError("stub")
def compile(pattern, *, flags=0):
    raise NotImplementedError("stub")
def escape(pattern, unix=None):
    raise NotImplementedError("stub")
def is_magic(pattern, *, flags=0):
    raise NotImplementedError("stub")

class WcMatcher:
    def __init__(self, pattern, flags=0):
        raise NotImplementedError("stub")
    def match(self, path):
        raise NotImplementedError("stub")
    def filter(self, paths):
        raise NotImplementedError("stub")

IGNORECASE = 1
EXTMATCH = 2
BRACE = 4
DOTMATCH = 8
GLOBSTAR = 16
PY_EOF

cat > wcmatch/pathlib.py << 'PY_EOF'
"""Stub pathlib module."""
import pathlib as _pathlib

class Path(_pathlib.PurePath):
    def match(self, pattern, *, flags=0):
        raise NotImplementedError("stub")

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
echo "Stub control installed"
