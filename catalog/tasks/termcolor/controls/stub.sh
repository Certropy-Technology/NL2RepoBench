#!/usr/bin/env bash
set -euo pipefail

# Stub control - minimal installable package with empty implementations
# Should collect all tests but fail most assertions

echo "=== Stub control ==="

mkdir -p /workspace/src/termcolor

cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools>=70", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "termcolor"
version = "1.0.0"
description = "Stub implementation"
requires-python = ">=3.10"
dependencies = []

[tool.setuptools.packages.find]
where = ["src"]
EOF

cat > /workspace/src/termcolor/__init__.py <<'EOF'
"""Stub termcolor implementation."""

COLORS = {}
HIGHLIGHTS = {}
ATTRIBUTES = {}
RESET = ""

def can_colorize(*, no_color=None, force_color=None):
    return False

def colored(text, color=None, on_color=None, attrs=None, *, no_color=None, force_color=None):
    return str(text)

def cprint(text, color=None, on_color=None, attrs=None, *, no_color=None, force_color=None, **kwargs):
    print(str(text), **kwargs)

__all__ = ["ATTRIBUTES", "COLORS", "HIGHLIGHTS", "RESET", "can_colorize", "colored", "cprint"]
EOF

cat > /workspace/src/termcolor/termcolor.py <<'EOF'
"""Stub termcolor module."""
from __future__ import annotations

COLORS = {}
HIGHLIGHTS = {}
ATTRIBUTES = {}
RESET = ""

def can_colorize(*, no_color=None, force_color=None):
    return False

def colored(text, color=None, on_color=None, attrs=None, *, no_color=None, force_color=None):
    return str(text)

def cprint(text, color=None, on_color=None, attrs=None, *, no_color=None, force_color=None, **kwargs):
    print(str(text), **kwargs)
EOF

echo "Stub package created"
pip install --no-cache-dir /workspace/ || exit 1
echo "Stub control complete - should collect tests but score low"
