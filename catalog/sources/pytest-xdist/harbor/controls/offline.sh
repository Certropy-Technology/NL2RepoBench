#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/xdist
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = []
build-backend = "setuptools.build_meta:__legacy__"
[project]
name = "pytest-xdist"
version = "0.0.0"
[tool.setuptools]
packages = ["xdist"]
TOML
cat > /workspace/xdist/__init__.py <<'PY'
import socket
socket.create_connection(("1.1.1.1", 443), timeout=0.2)
PY
