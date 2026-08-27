#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/src/pyrsistent
printf '%s\n' \
  '[build-system]' \
  'requires = ["setuptools==80.10.2", "wheel==0.45.1"]' \
  'build-backend = "setuptools.build_meta"' \
  '' \
  '[project]' \
  'name = "pyrsistent"' \
  'version = "0.21.0"' \
  'requires-python = ">=3.10"' \
  > /workspace/pyproject.toml
printf '%s\n' \
  '"""Importable but non-functional pyrsistent control."""' \
  '__all__ = ()' \
  > /workspace/src/pyrsistent/__init__.py
touch /workspace/src/pyrsistent/py.typed
touch /workspace/src/pyrsistent/__init__.pyi
touch /workspace/src/pyrsistent/typing.pyi
