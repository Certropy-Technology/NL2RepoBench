#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/exceptiongroup
cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(name="exceptiongroup", version="1.3.1.post6", packages=["exceptiongroup"])
PY
cat > /workspace/exceptiongroup/__init__.py <<'PY'
from builtins import BaseExceptionGroup, ExceptionGroup

__version__ = "1.3.1.post6"
__all__ = ["BaseExceptionGroup", "ExceptionGroup"]

def catch(*args, **kwargs):
    raise NotImplementedError("stub control")
PY
