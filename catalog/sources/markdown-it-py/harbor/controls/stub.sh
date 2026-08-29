#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/markdown_it
cat > /workspace/setup.py <<'PY'
from setuptools import setup
setup(name="markdown-it-py", version="4.2.0", packages=["markdown_it"])
PY
cat > /workspace/markdown_it/__init__.py <<'PY'
__version__ = "4.2.0"
__all__ = []
PY
