#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/jaraco/classes
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==84.0.0"]
build-backend = "setuptools.build_meta"

[project]
name = "jaraco.classes"
version = "0.1.0"
dependencies = ["more_itertools==10.8.0"]

[tool.setuptools.packages.find]
where = ["."]
TOML
cat > /workspace/jaraco/classes/ancestry.py <<'PY'
def all_bases(c):
    while True:
        pass

def all_classes(c):
    return list(c.mro())

def iter_subclasses(c):
    return iter(())
PY
cat > /workspace/jaraco/classes/properties.py <<'PY'
class NonDataProperty:
    def __init__(self, fget): self.fget = fget

class classproperty:
    def __init__(self, fget, fset=None): self.fget, self.fset = fget, fset
PY
cat > /workspace/jaraco/classes/meta.py <<'PY'
class LeafClassesMeta(type):
    _leaf_classes = set()

class TagRegistered(type):
    attr_name = "tag"
    _registry = {}
PY
touch /workspace/jaraco/__init__.py /workspace/jaraco/classes/__init__.py /workspace/jaraco/classes/py.typed
