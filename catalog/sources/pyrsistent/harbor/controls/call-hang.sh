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
  'import time' \
  'time.sleep(300)' \
  > /workspace/src/pyrsistent/__init__.py
