#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/dataclasses_json
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "dataclasses-json"
version = "0.0.0"
TOML
cat > /workspace/dataclasses_json/__init__.py <<'PY'
class DataClassJsonMixin:
    pass

def dataclass_json(cls=None, **kwargs):
    return cls if cls is not None else lambda value: value
PY
