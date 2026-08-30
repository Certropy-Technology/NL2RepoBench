#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/starlette
printf '[build-system]\nrequires = ["setuptools"]\nbuild-backend = "setuptools.build_meta"\n' > /workspace/pyproject.toml
printf 'import time; time.sleep(240)\n' > /workspace/setup.py
printf 'import time; time.sleep(240)\n' > /workspace/starlette/__init__.py
