#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
mkdir -p /workspace/src/urllib3
printf '%s\n' '[build-system]' 'requires = ["setuptools"]' 'build-backend = "setuptools.build_meta"' > /workspace/pyproject.toml
printf '%s\n' '[project]' 'name = "urllib3"' 'version = "2.7.1.dev42"' 'requires-python = ">=3.10"' > /workspace/pyproject.toml.tmp
cat /workspace/pyproject.toml.tmp >> /workspace/pyproject.toml
printf '%s\n' 'from ._version import __version__' '__all__ = ["__version__"]' > /workspace/src/urllib3/__init__.py
printf '%s\n' '__version__ = "2.7.1.dev42"' > /workspace/src/urllib3/_version.py
rm /workspace/pyproject.toml.tmp
