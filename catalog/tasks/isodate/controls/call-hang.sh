#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace
mkdir -p /workspace/isodate
printf '%s\n' '[build-system]' 'requires = []' 'build-backend = "setuptools.build_meta:__legacy__"' '[project]' 'name = "isodate"' 'version = "0.0.0"' > /workspace/pyproject.toml
printf '%s\n' 'import time' 'time.sleep(600)' > /workspace/isodate/__init__.py
