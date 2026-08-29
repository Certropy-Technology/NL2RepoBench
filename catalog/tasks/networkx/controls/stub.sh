#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
mkdir -p /workspace/networkx
cat > /workspace/networkx/__init__.py <<'PY'
__version__ = "0.0.0-stub"
class Graph:
    def __init__(self, *args, **kwargs):
        self.nodes = []
        self.edges = []
def path_graph(*args, **kwargs):
    return Graph()
PY
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
[project]
name = "networkx"
version = "0.0.0"
TOML
