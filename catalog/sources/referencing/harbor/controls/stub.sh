#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/referencing
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["hatchling==1.27.0"]
build-backend = "hatchling.build"

[project]
name = "referencing"
version = "0.1.0"
requires-python = ">=3.13"
TOML
cat > /workspace/referencing/__init__.py <<'PY'
__all__ = ["Anchor", "Registry", "Resource", "Specification"]

class Resource:
    @classmethod
    def opaque(cls, contents):
        value = cls()
        value.contents = contents
        return value

class Registry(dict):
    pass

class Specification:
    pass

class Anchor:
    pass
PY
