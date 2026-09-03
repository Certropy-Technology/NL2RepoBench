#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/arrow
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["flit_core==3.12.0"]
build-backend = "flit_core.buildapi"

[project]
name = "arrow"
version = "0.0.0"
description = "stub"
TOML
cat > /workspace/arrow/__init__.py <<'PY'
__version__ = "0.0.0"
PY
