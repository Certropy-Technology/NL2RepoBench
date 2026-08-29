#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/mdurl
printf '%s\n' '[build-system]' 'requires = []' 'build-backend = "mdurl_backend"' 'backend-path = ["."]' '' '[project]' 'name = "mdurl"' 'version = "0.1.2"' 'description = "install timeout control"' 'requires-python = ">=3.10"' > /workspace/pyproject.toml
printf '%s\n' 'import time' 'def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):' '    time.sleep(600)' > /workspace/mdurl_backend.py
printf '%s\n' '__version__ = "0.1.2"' > /workspace/src/mdurl/__init__.py
touch /workspace/src/mdurl/py.typed
