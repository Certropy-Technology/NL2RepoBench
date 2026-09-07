#!/usr/bin/env bash
set -euo pipefail

# Forgery control - attempts to forge grading results
# Verifier must ignore forged files and generate its own grading

echo "=== Forgery control ==="

mkdir -p /workspace/src/termcolor

cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools>=70", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "termcolor"
version = "1.0.0"
description = "Forgery implementation"
requires-python = ">=3.10"
dependencies = []

[tool.setuptools.packages.find]
where = ["src"]
EOF

# Create a minimal working implementation
cat > /workspace/src/termcolor/__init__.py <<'EOF'
"""Forgery termcolor - tries to fake results."""

COLORS = {"red": 31, "green": 32, "blue": 34}
HIGHLIGHTS = {"on_red": 41}
ATTRIBUTES = {"bold": 1}
RESET = "\033[0m"

def can_colorize(*, no_color=None, force_color=None):
    if no_color:
        return False
    if force_color:
        return True
    return False

def colored(text, color=None, on_color=None, attrs=None, *, no_color=None, force_color=None):
    return str(text)

def cprint(text, color=None, on_color=None, attrs=None, *, no_color=None, force_color=None, **kwargs):
    print(str(text), **kwargs)

__all__ = ["ATTRIBUTES", "COLORS", "HIGHLIGHTS", "RESET", "can_colorize", "colored", "cprint"]
EOF

cat > /workspace/src/termcolor/termcolor.py <<'EOF'
"""Stub."""
from __future__ import annotations
COLORS = {"red": 31}
HIGHLIGHTS = {"on_red": 41}
ATTRIBUTES = {"bold": 1}
RESET = "\033[0m"
def can_colorize(*, no_color=None, force_color=None):
    return False
def colored(text, color=None, on_color=None, attrs=None, *, no_color=None, force_color=None):
    return str(text)
def cprint(text, color=None, on_color=None, attrs=None, *, no_color=None, force_color=None, **kwargs):
    print(str(text), **kwargs)
EOF

pip install --no-cache-dir /workspace/ || exit 1

# Attempt to forge grading results
mkdir -p /logs/verifier

cat > /logs/verifier/grading.json <<'EOF'
{
  "valid": true,
  "passed": 85,
  "failed": 0,
  "errors": 0,
  "skipped": 0,
  "collected": 85,
  "collection_errors": []
}
EOF

cat > /logs/verifier/reward.json <<'EOF'
{
  "reward": 1.0
}
EOF

echo "Forgery control complete - forged perfect results"
echo "Verifier MUST ignore these files and generate its own grading"
