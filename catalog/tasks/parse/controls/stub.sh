#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools==80.10.2", "wheel==0.45.1"]
build-backend = "setuptools.build_meta"

[project]
name = "parse"
version = "1.20.2"
EOF
cat > /workspace/parse.py <<'EOF'
"""Importable but non-functional control implementation."""

class Result:
    def __init__(self, fixed=(), named=None, spans=None):
        self.fixed = tuple(fixed)
        self.named = {} if named is None else named
        self.spans = spans

def parse(*args, **kwargs):
    return None

search = parse

def findall(*args, **kwargs):
    return iter(())

def compile(*args, **kwargs):
    return object()

Parser = compile
EOF
