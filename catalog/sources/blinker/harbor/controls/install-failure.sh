#!/usr/bin/env bash
# Install failure: broken package metadata
set -euo pipefail

mkdir -p /workspace/src/blinker

cat > /workspace/src/blinker/__init__.py << 'INIT'
raise RuntimeError("Installation failed")
INIT

cat > /workspace/pyproject.toml << 'TOML'
[project]
name = "blinker"
version = "invalid version string"

[build-system]
requires = ["nonexistent-backend"]
build-backend = "nonexistent_backend"
TOML

# This should fail
python -m pip install --no-build-isolation --no-deps --no-index -e /workspace || true
