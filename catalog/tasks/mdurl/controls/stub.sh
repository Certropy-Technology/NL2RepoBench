#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/mdurl
printf '%s\n' '[build-system]' 'requires = ["flit_core==3.12.0"]' 'build-backend = "flit_core.buildapi"' '' '[project]' 'name = "mdurl"' 'version = "0.1.2"' 'requires-python = ">=3.10"' > /workspace/pyproject.toml
printf '%s\n' 'description = "stub"' 'authors = [{name = "control"}]' >> /workspace/pyproject.toml
printf '%s\n' '__version__ = "0.1.2"' '__all__ = ()' > /workspace/src/mdurl/__init__.py
touch /workspace/src/mdurl/py.typed
