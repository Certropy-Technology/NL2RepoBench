#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/pygments
printf '%s\n' '[build-system]' 'requires = ["setuptools==80.10.2", "wheel==0.45.1"]' 'build-backend = "setuptools.build_meta"' '[project]' 'name = "Pygments"' 'version = "2.21.0"' > /workspace/pyproject.toml
printf '%s\n' '__version__ = "2.21.0"' 'def lex(*args, **kwargs):' '    while True: pass' > /workspace/pygments/__init__.py
