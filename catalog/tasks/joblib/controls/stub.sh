#!/usr/bin/env bash
set -euo pipefail

cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==84.0.0"]
build-backend = "setuptools.build_meta"

[project]
name = "joblib"
version = "1.6.dev0"

[tool.setuptools]
packages = ["joblib"]
TOML

mkdir -p /workspace/joblib
cat > /workspace/joblib/__init__.py <<'PY'
__version__ = "1.6.dev0"

def delayed(function):
    return function

class Parallel:
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, iterable):
        return list(iterable)
PY
