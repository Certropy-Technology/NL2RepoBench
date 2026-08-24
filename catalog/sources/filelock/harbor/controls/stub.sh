#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/src/filelock
printf '%s\n' \
  '[build-system]' \
  'requires = ["setuptools==75.8.0", "wheel==0.45.1"]' \
  'build-backend = "setuptools.build_meta"' \
  '' \
  '[project]' \
  'name = "filelock"' \
  'version = "3.32.3"' \
  'requires-python = ">=3.10"' \
  '' \
  '[tool.setuptools.packages.find]' \
  'where = ["src"]' \
  > /workspace/pyproject.toml
printf '%s\n' \
  '"""Importable non-functional filelock control package."""' \
  '__version__ = "3.32.3"' \
  > /workspace/src/filelock/__init__.py
