#!/bin/bash
set -euo pipefail

# Create an invalid package that will fail to install
mkdir -p /workspace/src/chardet
cat > /workspace/pyproject.toml << 'PYPROJECT_EOF'
[project]
name = "chardet"
version = "7.6.0"
description = "Invalid package"
INVALID SYNTAX HERE
PYPROJECT_EOF

python -m pip install --no-build-isolation --no-deps --no-index -e /workspace || true
