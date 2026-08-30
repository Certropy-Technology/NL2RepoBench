#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/virtualenv
printf '%s\n' '[build-system]' 'requires = ["setuptools"]' 'build-backend = "setuptools.build_meta"' '[project]' 'name = "virtualenv"' 'version = "21.7.5"' > /workspace/pyproject.toml
printf '%s\n' 'import time' 'time.sleep(600)' > /workspace/virtualenv/__init__.py
