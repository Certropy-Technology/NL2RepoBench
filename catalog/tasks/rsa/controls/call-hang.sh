#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/rsa
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["poetry-core==1.9.1"]
build-backend = "poetry.core.masonry.api"
[tool.poetry]
name = "rsa"
version = "4.10-dev0"
description = "call hang control"
authors = ["control"]
packages = [{ include = "rsa" }]
[tool.poetry.dependencies]
python = ">=3.8,<4"
pyasn1 = ">=0.1.3"
EOF
cat > /workspace/rsa/__init__.py <<'EOF'
import time
time.sleep(600)
EOF
