#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/sqlparse
cat > /workspace/pyproject.toml <<'PYPROJECT'
[build-system]
requires = ["hatchling==1.27.0"]
build-backend = "hatchling.build"
[project]
name = "sqlparse"
version = "0.5.4.dev0"
requires-python = ">=3.8"
PYPROJECT
cat > /workspace/sqlparse/__init__.py <<'PY'
__version__ = "0.5.4.dev0"
__all__ = []
def parse(value, encoding=None): return ()
def parsestream(value, encoding=None): return iter(())
def split(value, encoding=None, strip_semicolon=False): return []
def format(value, encoding=None, **options): return value
PY
