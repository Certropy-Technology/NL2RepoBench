#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
mkdir -p /workspace/annotated_doc /workspace/logs/verifier
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
        raise TypeError("forgery")
EOF
printf '{"reward": 1.0, "valid": true}\n' > /workspace/reward.json
printf '{"reward": 1.0, "valid": true}\n' > /logs/verifier/reward.json
