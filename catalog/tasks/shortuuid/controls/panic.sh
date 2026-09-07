#!/bin/bash
set -euo pipefail

echo "[control:panic] Creating package that panics on import"

cd /workspace

cat > pyproject.toml << 'PYPROJECT'
[tool.poetry]
name = "shortuuid"
version = "1.0.13"
description = "Panic control"
license = "BSD-3-Clause"
authors = ["Panic <panic@example.com>"]

[tool.poetry.scripts]
shortuuid = "shortuuid.cli:cli"

[tool.poetry.dependencies]
python = ">=3.6"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
PYPROJECT

mkdir -p shortuuid

cat > shortuuid/__init__.py << 'INIT'
"""Panic on import."""
import sys
print("PANIC: Exiting immediately", file=sys.stderr)
sys.exit(1)
INIT

touch shortuuid/py.typed

echo "[control:panic] Panic implementation created"
