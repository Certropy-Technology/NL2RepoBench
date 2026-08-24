#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/src/ministats

cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools>=70", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "ministats-bench"
version = "1.0.0"
dependencies = []

[tool.setuptools.packages.find]
where = ["src"]
EOF

cat > /workspace/src/ministats/__init__.py <<'EOF'
import time

__version__ = "1.0.0"
__all__ = ["__version__", "normalize", "summarize", "tokenize"]


def _hang():
    time.sleep(9)


def normalize(text):
    _hang()


def tokenize(text):
    _hang()


def summarize(text, top=3):
    _hang()
EOF
