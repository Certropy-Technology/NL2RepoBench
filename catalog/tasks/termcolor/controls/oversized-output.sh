#!/usr/bin/env bash
set -euo pipefail

# Oversized output control - candidate that produces excessive output
# Verifier should handle output size limits

echo "=== Oversized output control ==="

mkdir -p /workspace/src/termcolor

cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools>=70", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "termcolor"
version = "1.0.0"
description = "Oversized output implementation"
requires-python = ">=3.10"
dependencies = []

[tool.setuptools.packages.find]
where = ["src"]
EOF

cat > /workspace/src/termcolor/__init__.py <<'EOF'
"""Oversized output on function call."""

COLORS = {"red": 31}
HIGHLIGHTS = {"on_red": 41}
ATTRIBUTES = {"bold": 1}
RESET = "\033[0m"

def can_colorize(*, no_color=None, force_color=None):
    for i in range(100000):
        print(f"SPAM LINE {i}" * 100)
    return False

def colored(text, color=None, on_color=None, attrs=None, *, no_color=None, force_color=None):
    for i in range(100000):
        print(f"EXCESSIVE OUTPUT {i}" * 100)
    return str(text)

def cprint(text, color=None, on_color=None, attrs=None, *, no_color=None, force_color=None, **kwargs):
    for i in range(100000):
        print(f"TOO MUCH DATA {i}" * 100)

__all__ = ["ATTRIBUTES", "COLORS", "HIGHLIGHTS", "RESET", "can_colorize", "colored", "cprint"]
EOF

cat > /workspace/src/termcolor/termcolor.py <<'EOF'
COLORS = {}
HIGHLIGHTS = {}
ATTRIBUTES = {}
RESET = ""
def can_colorize(*, no_color=None, force_color=None):
    return False
def colored(text, color=None, on_color=None, attrs=None, *, no_color=None, force_color=None):
    return str(text)
def cprint(text, color=None, on_color=None, attrs=None, *, no_color=None, force_color=None, **kwargs):
    pass
EOF

pip install --no-cache-dir /workspace/ || exit 1
echo "Oversized output control complete - will spam stdout"
