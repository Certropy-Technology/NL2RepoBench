#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/coverage
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==84.0.0"]
build-backend = "setuptools.build_meta"

[project]
name = "coverage"
version = "7.16.0a0.dev1"

[tool.setuptools]
packages = ["coverage"]
TOML
cat > /workspace/coverage/__init__.py <<'PY'
class Coverage:
    pass
class CoverageData:
    pass
PY
