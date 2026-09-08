#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/wcmatch
cd /workspace

cat > wcmatch/__init__.py << 'PY_EOF'
"""Panic control."""
__version__ = "11.0.1"
PY_EOF

cat > wcmatch/fnmatch.py << 'PY_EOF'
"""Panic fnmatch module."""
import sys
def fnmatch(name, pattern, *, flags=0):
    sys.exit(42)
def filter(names, pattern, *, flags=0):
    raise SystemExit(42)
def translate(pattern, *, flags=0):
    raise SystemExit(42)
def compile(pattern, *, flags=0):
    raise SystemExit(42)
def escape(pattern):
    raise SystemExit(42)
def is_magic(pattern, *, flags=0):
    raise SystemExit(42)

class WcMatcher:
    def __init__(self, pattern, flags=0):
        raise SystemExit(42)
    def match(self, name):
        raise SystemExit(42)
    def filter(self, names):
        raise SystemExit(42)

IGNORECASE = 1
EXTMATCH = 2
BRACE = 4
DOTMATCH = 8
NEGATE = 16
NEGATEALL = 32
SPLIT = 64
PY_EOF

cat > wcmatch/glob.py << 'PY_EOF'
"""Panic glob module."""
import sys
def globmatch(path, pattern, *, flags=0):
    sys.exit(42)
def globfilter(paths, pattern, *, flags=0):
    raise SystemExit(42)
def translate(pattern, *, flags=0):
    raise SystemExit(42)
def compile(pattern, *, flags=0):
    raise SystemExit(42)
def escape(pattern, unix=None):
    raise SystemExit(42)
def is_magic(pattern, *, flags=0):
    raise SystemExit(42)

class WcMatcher:
    def __init__(self, pattern, flags=0):
        raise SystemExit(42)
    def match(self, path):
        raise SystemExit(42)
    def filter(self, paths):
        raise SystemExit(42)

IGNORECASE = 1
EXTMATCH = 2
BRACE = 4
DOTMATCH = 8
GLOBSTAR = 16
PY_EOF

cat > wcmatch/pathlib.py << 'PY_EOF'
"""Panic pathlib module."""
import pathlib as _pathlib
import sys

class Path(_pathlib.PurePath):
    def match(self, pattern, *, flags=0):
        sys.exit(42)

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
echo "Panic control installed"
