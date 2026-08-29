#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
mkdir -p /workspace/networkx
cat > /workspace/networkx/__init__.py <<'PY'
__version__ = "0.0.0"
class Graph:
    def __init__(self, *args, **kwargs):
        while True:
            pass
def __getattr__(name):
    while True:
        pass
PY
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"
[project]
name = "networkx"
version = "0.0.0"
TOML
