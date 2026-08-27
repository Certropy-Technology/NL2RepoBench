#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/fastjsonschema
cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(name="fastjsonschema", version="2.22.2", packages=["fastjsonschema"])
PY
cat > /workspace/fastjsonschema/__init__.py <<'PY'
VERSION = "2.22.2"

def validate(*args, **kwargs):
    raise NotImplementedError("stub control")

def compile(*args, **kwargs):
    raise NotImplementedError("stub control")

def compile_to_code(*args, **kwargs):
    raise NotImplementedError("stub control")
PY
