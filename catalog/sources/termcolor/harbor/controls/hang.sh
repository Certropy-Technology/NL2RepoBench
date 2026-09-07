#!/usr/bin/env bash
set -euo pipefail

# Hang control - candidate that hangs on function call
# Verifier should timeout gracefully

echo "=== Hang control ==="

mkdir -p /workspace/src/termcolor

cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools>=70", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "termcolor"
version = "1.0.0"
description = "Hang implementation"
requires-python = ">=3.10"
dependencies = []

[tool.setuptools.packages.find]
where = ["src"]
EOF

cat > /workspace/src/termcolor/__init__.py <<'EOF'
"""Hang on function call."""
import time

COLORS = {"red": 31}
HIGHLIGHTS = {"on_red": 41}
ATTRIBUTES = {"bold": 1}
RESET = "\033[0m"

def can_colorize(*, no_color=None, force_color=None):
    time.sleep(999999)
    return False

def colored(text, color=None, on_color=None, attrs=None, *, no_color=None, force_color=None):
    time.sleep(999999)
    return str(text)

def cprint(text, color=None, on_color=None, attrs=None, *, no_color=None, force_color=None, **kwargs):
    time.sleep(999999)

__all__ = ["ATTRIBUTES", "COLORS", "HIGHLIGHTS", "RESET", "can_colorize", "colored", "cprint"]
EOF

cat > /workspace/src/termcolor/termcolor.py <<'EOF'
import time
COLORS = {}
HIGHLIGHTS = {}
ATTRIBUTES = {}
RESET = ""
def can_colorize(*, no_color=None, force_color=None):
    time.sleep(999999)
def colored(text, color=None, on_color=None, attrs=None, *, no_color=None, force_color=None):
    time.sleep(999999)
def cprint(text, color=None, on_color=None, attrs=None, *, no_color=None, force_color=None, **kwargs):
    time.sleep(999999)
EOF

pip install --no-cache-dir /workspace/ || exit 1
echo "Hang control complete - will hang on function calls"
