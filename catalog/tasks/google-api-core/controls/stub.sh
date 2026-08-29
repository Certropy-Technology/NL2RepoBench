#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/google/api_core
printf '%s\n' '[build-system]' 'requires = ["setuptools"]' 'build-backend = "setuptools.build_meta"' '[project]' 'name = "google-api-core"' 'version = "2.35.0"' > /workspace/pyproject.toml
printf '%s\n' '__version__ = "2.35.0"' > /workspace/google/api_core/__init__.py
