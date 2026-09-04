#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
mkdir -p /workspace/annotated_doc
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools>=70", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "annotated-doc"
version = "0.0.5"
requires-python = ">=3.9"

[tool.setuptools]
packages = ["annotated_doc"]
EOF
cat > /workspace/annotated_doc/__init__.py <<'EOF'
__version__ = "0.0.0"
class Doc:
    def __init__(self, *args, **kwargs):
        raise TypeError("stub")
EOF
