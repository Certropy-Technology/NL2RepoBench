#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/src/editables
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["flit_core==3.12.0"]
build-backend = "flit_core.buildapi"

[project]
name = "editables"
version = "0.6"
description = "Importable control stub"
TOML
cat > /workspace/src/editables/__init__.py <<'PY'
__version__ = "0.6"
class EditableException(Exception):
    pass
class EditableProject:
    pass
PY
