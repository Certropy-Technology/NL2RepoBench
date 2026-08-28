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
requires-python = ">=3.10"

[tool.setuptools]
packages = ["frozenlist"]

[tool.setuptools.package-data]
frozenlist = ["py.typed", "__init__.pyi"]
TOML
cat > /workspace/frozenlist/__init__.py <<'PY'
__version__ = "1.8.1.dev0"
__all__ = ("FrozenList", "PyFrozenList")

class FrozenList:
    def __init__(self, items=None):
        self.items = list(items or ())

PyFrozenList = FrozenList
PY
printf 'Marker\n' > /workspace/frozenlist/py.typed
printf 'class FrozenList: ...\nPyFrozenList = FrozenList\n' > /workspace/frozenlist/__init__.pyi
