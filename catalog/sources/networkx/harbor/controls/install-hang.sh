#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
mkdir -p /workspace/networkx
cat > /workspace/networkx/__init__.py <<'PY'
import time
time.sleep(600)
PY
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"
[project]
name = "networkx"
version = "0.0.0"
TOML
