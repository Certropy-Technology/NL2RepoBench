#!/usr/bin/env bash
set -euo pipefail

cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "tqdm"
version = "0.0.1"
TOML
mkdir -p /workspace/tqdm
cat > /workspace/tqdm/__init__.py <<'PY'
__version__ = "0.0.1"
PY
