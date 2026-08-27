#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace
mkdir -p /workspace/iso8601
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
name = "iso8601"
version = "2.1.0"
description = "timeout control"
authors = []
packages = [{ include = "iso8601" }]
TOML
cat > /workspace/iso8601/__init__.py <<'PY'
import time
time.sleep(600)
PY
