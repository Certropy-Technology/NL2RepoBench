#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==80.9.0"]
build-backend = "setuptools.build_meta"
[project]
name = "propcache"
version = "0.0.0"
[tool.setuptools]
packages = ["propcache"]
TOML
mkdir -p /workspace/propcache
cat > /workspace/propcache/__init__.py <<'PY'
import time

__version__ = "0.0.0"
class cached_property:
    def __init__(self, func):
        self.func = func
    def __get__(self, instance, owner=None):
        time.sleep(3600)
class under_cached_property(cached_property):
    pass
PY
