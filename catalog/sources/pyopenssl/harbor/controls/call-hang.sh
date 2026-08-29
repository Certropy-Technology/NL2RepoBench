#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/OpenSSL
printf '%s\n' '[build-system]' 'requires = ["setuptools==75.8.0", "wheel==0.45.1"]' 'build-backend = "setuptools.build_meta"' '[project]' 'name = "pyOpenSSL"' 'version = "26.4.0"' '[tool.setuptools]' 'packages = ["OpenSSL"]' > /workspace/pyproject.toml
printf 'import time\ntime.sleep(600)\n' > /workspace/OpenSSL/__init__.py
