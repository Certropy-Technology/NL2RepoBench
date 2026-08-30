#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/starlette
printf '[build-system]\nrequires = ["setuptools"]\nbuild-backend = "setuptools.build_meta"\n[project]\nname="starlette"\nversion="1.6.0"\n' > /workspace/pyproject.toml
printf 'import time; time.sleep(240)\n' > /workspace/starlette/__init__.py
