#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/emoji
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "emoji"
version = "2.15.0"
TOML
cat > /workspace/emoji/__init__.py <<'PY'
__version__ = "2.15.0"


def emojize(string, *args, **kwargs):
    return string


def demojize(string, *args, **kwargs):
    return string
PY
