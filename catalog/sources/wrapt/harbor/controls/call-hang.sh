#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/wrapt
printf '%s\n' '[build-system]' 'requires = ["setuptools==84.0.0"]' 'build-backend = "setuptools.build_meta"' > /workspace/pyproject.toml
printf '%s\n' '[project]' 'name = "wrapt"' 'version = "2.4.0rc5"' >> /workspace/pyproject.toml
cat > /workspace/wrapt/__init__.py <<'PY'
import time
time.sleep(120)
PY
