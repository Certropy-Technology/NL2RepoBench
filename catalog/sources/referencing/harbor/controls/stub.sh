#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/referencing
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==84.0.0"]
build-backend = "setuptools.build_meta"

[project]
name = "referencing"
version = "0.0.0"
TOML
cat > /workspace/referencing/__init__.py <<'PY'
__all__ = ["Anchor", "Registry", "Resource", "Specification"]
class Anchor: pass
class Registry: pass
class Resource: pass
class Specification: pass
PY
