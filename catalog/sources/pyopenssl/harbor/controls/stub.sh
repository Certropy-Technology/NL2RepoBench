#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/OpenSSL
printf '%s\n' '[build-system]' 'requires = ["setuptools==75.8.0", "wheel==0.45.1"]' 'build-backend = "setuptools.build_meta"' '[project]' 'name = "pyOpenSSL"' 'version = "26.4.0"' 'dependencies = ["cryptography>=49.0.0,<51"]' '[tool.setuptools]' 'packages = ["OpenSSL"]' > /workspace/pyproject.toml
printf '__version__ = "26.4.0"\n' > /workspace/OpenSSL/__init__.py
