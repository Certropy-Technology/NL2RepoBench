#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/wrapt
printf '%s\n' '[build-system]' 'requires = ["setuptools==84.0.0"]' 'build-backend = "setuptools.build_meta"' > /workspace/pyproject.toml
printf '%s\n' '[project]' 'name = "wrapt"' 'version = "2.4.0rc5"' >> /workspace/pyproject.toml
printf '%s\n' '__version__ = "2.4.0rc5"' 'class ObjectProxy: pass' > /workspace/wrapt/__init__.py
