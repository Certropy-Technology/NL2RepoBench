#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/src/prompt_toolkit
cat > /workspace/pyproject.toml <<'PYPROJECT'
[build-system]
requires = ["setuptools==80.10.2"]
build-backend = "setuptools.build_meta"

[project]
name = "prompt_toolkit"
version = "3.0.53"
requires-python = ">=3.10"

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
PYPROJECT

cat > /workspace/src/prompt_toolkit/__init__.py <<'PACKAGE'
__version__ = "3.0.53"
VERSION = (3, 0, 53)
PACKAGE
