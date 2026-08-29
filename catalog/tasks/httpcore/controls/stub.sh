#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/httpcore
printf '%s\n' '[build-system]' 'requires = ["hatchling"]' 'build-backend = "hatchling.build"' > /workspace/pyproject.toml
printf '%s\n' '[project]' 'name = "httpcore"' 'version = "0.0.0"' 'requires-python = ">=3.12"' >> /workspace/pyproject.toml
printf '%s\n' '__version__ = "0.0.0"' > /workspace/httpcore/__init__.py
