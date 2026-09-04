#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
mkdir -p /workspace/multidict
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==84.0.0"]
build-backend = "setuptools.build_meta"
[project]
name = "multidict"
version = "6.7.2.dev0"
[tool.setuptools]
packages = ["multidict"]
[tool.setuptools.package-data]
multidict = ["py.typed"]
TOML
cat > /workspace/multidict/__init__.py <<'PY'
__version__ = "6.7.2.dev0"
__all__ = ("CIMultiDict", "CIMultiDictProxy", "MultiDict", "MultiDictProxy", "MultiMapping", "MutableMultiMapping", "getversion", "istr", "upstr")
class MultiMapping: pass
class MutableMultiMapping: pass
class MultiDict(dict):
    def __init__(self, *args, **kwargs): raise TypeError("stub")
class CIMultiDict(MultiDict): pass
class MultiDictProxy(MultiMapping):
    def __init__(self, value): raise TypeError("stub")
class CIMultiDictProxy(MultiDictProxy): pass
class istr(str): pass
upstr = istr
def getversion(value): raise TypeError("stub")
PY
: > /workspace/multidict/py.typed
