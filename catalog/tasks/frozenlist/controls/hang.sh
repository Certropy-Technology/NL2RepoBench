#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/frozenlist
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==84.0.0"]
build-backend = "setuptools.build_meta"
[project]
name = "frozenlist"
version = "1.8.1.dev0"
[tool.setuptools]
packages = ["frozenlist"]
TOML
cat > /workspace/frozenlist/__init__.py <<'PY'
import time
__version__ = "1.8.1.dev0"
__all__ = ("FrozenList", "PyFrozenList")
class FrozenList(list):
    def __init__(self, items=None):
        super().__init__(items or ())
        self.frozen = False
    def __class_getitem__(cls, item):
        while True:
            time.sleep(1)
    def freeze(self):
        self.frozen = True
PyFrozenList = FrozenList
PY
