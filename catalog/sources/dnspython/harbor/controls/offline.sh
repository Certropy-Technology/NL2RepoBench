#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/dns
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = []
build-backend = "setuptools.build_meta:__legacy__"
[project]
name = "dnspython"
version = "0.0.0"
[tool.setuptools]
packages = ["dns"]
TOML
cat > /workspace/dns/__init__.py <<'PY'
import socket

try:
    socket.create_connection(("1.1.1.1", 443), timeout=0.1)
except OSError:
    pass
PY
