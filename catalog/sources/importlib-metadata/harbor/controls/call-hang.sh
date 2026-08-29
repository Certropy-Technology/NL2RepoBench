#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/importlib_metadata
cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(name="importlib_metadata", version="8.9.1.dev28", packages=["importlib_metadata"])
PY
cat > /workspace/importlib_metadata/__init__.py <<'PY'
__all__ = []


def version(name):
    while True:
        pass
PY
