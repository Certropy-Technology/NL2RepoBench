#!/usr/bin/env bash
set -euo pipefail

# Importable package with no parser behavior. The frozen suite must stay at
# its full denominator and report failures rather than collection shrinkage.
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/src/parsy
printf '%s\n' \
  '[build-system]' \
  'requires = ["setuptools==80.10.2", "wheel==0.45.1"]' \
  'build-backend = "setuptools.build_meta"' \
  '' \
  '[project]' \
  'name = "parsy"' \
  'version = "2.2"' \
  > /workspace/pyproject.toml
printf '%s\n' \
  '"""Non-functional parsy control package."""' \
  '__version__ = "2.2"' \
  > /workspace/src/parsy/__init__.py
