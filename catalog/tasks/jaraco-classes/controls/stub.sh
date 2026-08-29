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
printf 'def all_bases(c): return []\ndef all_classes(c): return []\ndef iter_subclasses(c): return iter(())\n' > /workspace/jaraco/classes/ancestry.py
printf 'class NonDataProperty: pass\nclass classproperty: pass\n' > /workspace/jaraco/classes/properties.py
printf 'class LeafClassesMeta(type): pass\nclass TagRegistered(type): pass\n' > /workspace/jaraco/classes/meta.py
touch /workspace/jaraco/__init__.py /workspace/jaraco/classes/__init__.py /workspace/jaraco/classes/py.typed
