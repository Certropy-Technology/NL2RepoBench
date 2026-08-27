#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/src/sympy_slice
cat > /workspace/setup.py <<'PY'
from setuptools import find_packages, setup

setup(name="sympy-bounded", version="0.1.0", package_dir={"": "src"}, packages=find_packages("src"))
PY
cat > /workspace/src/sympy_slice/__init__.py <<'PY'
import time

def parse_expression(expression):
    time.sleep(600)
    return str(expression)
PY
