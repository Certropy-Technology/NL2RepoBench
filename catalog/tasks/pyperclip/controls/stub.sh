#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/pyperclip
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools>=70", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "pyperclip"
version = "1.11.0"
requires-python = ">=3.10"

[tool.setuptools]
packages = ["pyperclip"]
EOF

cat > /workspace/pyperclip/__init__.py <<'EOF'
__version__ = "1.11.0"
__all__ = ["copy", "paste", "set_clipboard", "determine_clipboard"]

def copy(text):
    raise NotImplementedError

def paste():
    raise NotImplementedError

def set_clipboard(name):
    raise NotImplementedError

def determine_clipboard():
    raise NotImplementedError
EOF
