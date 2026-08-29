#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/jaraco/functools
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==84.0.0"]
build-backend = "setuptools.build_meta"

[project]
name = "jaraco.functools"
version = "1.0.0"
requires-python = ">=3.10"

[tool.setuptools]
packages = ["jaraco", "jaraco.functools"]
TOML
printf '%s\n' '# stub' > /workspace/jaraco/__init__.py
printf '%s\n' '# intentionally incomplete' > /workspace/jaraco/functools/__init__.py
