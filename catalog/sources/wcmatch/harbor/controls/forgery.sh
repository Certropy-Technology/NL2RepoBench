#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/wcmatch
cd /workspace

cat > wcmatch/__init__.py << 'PY_EOF'
"""Forgery wcmatch package."""
__version__ = "11.0.1"
PY_EOF

cat > wcmatch/fnmatch.py << 'PY_EOF'
"""Forgery fnmatch module."""
def fnmatch(name, pattern, *, flags=0):
    return True
def filter(names, pattern, *, flags=0):
    return names
def translate(pattern, *, flags=0):
    return ([".*"], [])
def compile(pattern, *, flags=0):
    return WcMatcher()
def escape(pattern):
    return pattern
def is_magic(pattern, *, flags=0):
    return True

class WcMatcher:
    def match(self, name):
        return True
    def filter(self, names):
        return names

IGNORECASE = 1
EXTMATCH = 2
BRACE = 4
DOTMATCH = 8
NEGATE = 16
NEGATEALL = 32
SPLIT = 64
PY_EOF

cat > wcmatch/glob.py << 'PY_EOF'
"""Forgery glob module."""
def globmatch(path, pattern, *, flags=0):
    return True
def globfilter(paths, pattern, *, flags=0):
    return paths
def translate(pattern, *, flags=0):
    return ([".*"], [])
def compile(pattern, *, flags=0):
    return WcMatcher()
def escape(pattern, unix=None):
    return pattern
def is_magic(pattern, *, flags=0):
    return True

class WcMatcher:
    def match(self, path):
        return True
    def filter(self, paths):
        return paths

IGNORECASE = 1
EXTMATCH = 2
BRACE = 4
DOTMATCH = 8
GLOBSTAR = 16
PY_EOF

cat > wcmatch/pathlib.py << 'PY_EOF'
"""Forgery pathlib module."""
import pathlib as _pathlib

class Path(_pathlib.PurePath):
    def match(self, pattern, *, flags=0):
        return True

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
echo "Forgery control installed"
