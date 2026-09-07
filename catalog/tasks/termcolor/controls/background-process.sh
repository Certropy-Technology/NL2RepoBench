#!/usr/bin/env bash
set -euo pipefail

# Background process control - candidate that spawns background processes
# Verifier should clean up process groups

echo "=== Background process control ==="

mkdir -p /workspace/src/termcolor

cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools>=70", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "termcolor"
version = "1.0.0"
description = "Background process implementation"
requires-python = ">=3.10"
dependencies = []

[tool.setuptools.packages.find]
where = ["src"]
EOF

cat > /workspace/src/termcolor/__init__.py <<'EOF'
"""Spawns background processes."""
import subprocess
import sys

COLORS = {"red": 31}
HIGHLIGHTS = {"on_red": 41}
ATTRIBUTES = {"bold": 1}
RESET = "\033[0m"

def can_colorize(*, no_color=None, force_color=None):
    # Spawn background sleep process
    subprocess.Popen([sys.executable, "-c", "import time; time.sleep(3600)"])
    return False

def colored(text, color=None, on_color=None, attrs=None, *, no_color=None, force_color=None):
    subprocess.Popen([sys.executable, "-c", "import time; time.sleep(3600)"])
    return str(text)

def cprint(text, color=None, on_color=None, attrs=None, *, no_color=None, force_color=None, **kwargs):
    subprocess.Popen([sys.executable, "-c", "import time; time.sleep(3600)"])
    print(str(text), **kwargs)

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
echo "Background process control complete - will spawn subprocesses"
