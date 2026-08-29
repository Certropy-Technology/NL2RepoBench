#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/python_discovery
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["hatchling==1.28.0"]
build-backend = "hatchling.build"
[project]
name = "python-discovery"
version = "0.0.0"
requires-python = ">=3.8"
[tool.hatch.build.targets.wheel]
packages = ["src/python_discovery"]
EOF
cat > /workspace/src/python_discovery/__init__.py <<'EOF'
__version__ = "0.0.0"
EOF
