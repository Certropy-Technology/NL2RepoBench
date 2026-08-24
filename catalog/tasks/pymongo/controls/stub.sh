#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/pymongo /workspace/src/bson
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools>=65"]
build-backend = "setuptools.build_meta"
[project]
name = "pymongo"
version = "4.18.0.dev0"
[tool.setuptools.packages.find]
where = ["src"]
EOF
printf '__version__ = "4.18.0.dev0"\n' > /workspace/src/pymongo/__init__.py
printf '' > /workspace/src/bson/__init__.py
