#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/src/trove_classifiers
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools", "calver"]
build-backend = "setuptools.build_meta"
EOF
cat > /workspace/setup.py <<'PY'
from setuptools import find_packages, setup

setup(
    name="trove-classifiers",
    version="2026.6.1.19",
    package_dir={"": "src"},
    packages=find_packages("src"),
)
PY
cat > /workspace/src/trove_classifiers/__init__.py <<'PY'
"""Minimal installable negative-control package."""
PY
cat > /workspace/src/trove_classifiers/__main__.py <<'PY'
"""Minimal module entry point for the negative control."""
PY
