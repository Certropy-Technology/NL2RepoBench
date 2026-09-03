#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/requests_cache
printf '%s\n' 'from .session import CachedSession' > /workspace/requests_cache/__init__.py
printf '%s\n' 'class CachedSession: pass' > /workspace/requests_cache/session.py
printf '%s\n' '[build-system]' 'requires = ["hatchling==1.27.0"]' 'build-backend = "hatchling.build"' > /workspace/pyproject.toml
printf '%s\n' '[project]' 'name = "requests-cache"' 'version = "1.3.4"' 'requires-python = ">=3.12"' >> /workspace/pyproject.toml
