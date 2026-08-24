#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/attrs /workspace/attr
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==84.0.0"]
build-backend = "setuptools.build_meta"

[project]
name = "attrs"
version = "26.1.0"
requires-python = ">=3.10"

[tool.setuptools]
packages = ["attr", "attrs"]
TOML
cat > /workspace/attrs/__init__.py <<'PY'
NOTHING = object()
def define(cls=None, **kwargs):
    return cls if cls is not None else (lambda value: value)
def field(**kwargs):
    return None
def fields(value):
    return ()
PY
cat > /workspace/attr/__init__.py <<'PY'
from attrs import *
s = attrs = define
ib = attrib = field
PY
