#!/usr/bin/env bash
set -euo pipefail

cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(name="ruff", version="0.16.4", packages=["ruff"], entry_points={"console_scripts": ["ruff=ruff.cli:main"]})
PY
mkdir -p /workspace/ruff
cat > /workspace/ruff/__init__.py <<'PY'
__version__ = "0.16.4"
PY
cat > /workspace/ruff/cli.py <<'PY'
import time


def main():
    time.sleep(60)
    return 0
PY
