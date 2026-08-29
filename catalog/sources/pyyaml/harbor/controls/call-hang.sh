#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/yaml
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==84.0.0", "wheel==0.48.0"]
build-backend = "setuptools.build_meta"

[project]
name = "PyYAML"
version = "7.0.0.dev0"

[tool.setuptools]
packages = ["yaml"]
TOML
cat > /workspace/yaml/__init__.py <<'PY'
import time

__version__ = "7.0.0.dev0"


def __getattr__(name):
    time.sleep(9)
    raise AttributeError(name)
PY
