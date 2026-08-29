#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/idna
printf '%s\n' '[build-system]' 'requires = ["flit_core"]' 'build-backend = "flit_core.buildapi"' > /workspace/pyproject.toml
printf '%s\n' '[project]' 'name = "idna"' 'version = "3.19"' 'description = "control"' 'requires-python = ">=3.9"' >> /workspace/pyproject.toml
printf '%s\n' 'class IDNAError(UnicodeError): pass' '__version__ = "3.19"' > /workspace/idna/__init__.py

