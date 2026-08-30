#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/tiktoken
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
[project]
name = "tiktoken"
version = "0.14.0"
EOF
cat > /workspace/tiktoken/__init__.py <<'EOF'
__version__ = "0.14.0"
class Encoding:
    def __init__(self, *args, **kwargs): pass
def get_encoding(name): raise ValueError(name)
def encoding_for_model(name): raise KeyError(name)
def encoding_name_for_model(name): raise KeyError(name)
def list_encoding_names(): return []
EOF
