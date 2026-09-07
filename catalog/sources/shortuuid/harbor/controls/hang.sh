#!/bin/bash
set -euo pipefail

echo "[control:hang] Creating package that hangs on import"

cd /workspace

cat > pyproject.toml << 'PYPROJECT'
[tool.poetry]
name = "shortuuid"
version = "1.0.13"
description = "Hang control"
license = "BSD-3-Clause"
authors = ["Hang <hang@example.com>"]

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
"""Hang beyond the candidate cumulative budget."""
import time
print("Hanging...")
time.sleep(400)
INIT

touch shortuuid/py.typed

echo "[control:hang] Hang implementation created"
