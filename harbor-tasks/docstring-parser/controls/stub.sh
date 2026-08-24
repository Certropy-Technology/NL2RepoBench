#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/docstring_parser
cat > /workspace/pyproject.toml <<'PYPROJECT'
[build-system]
requires = ["hatchling==1.27.0"]
build-backend = "hatchling.build"
[project]
name = "docstring_parser"
version = "0.18.0"
requires-python = ">=3.8"
[tool.hatch.build.targets.wheel]
packages = ["docstring_parser"]
PYPROJECT
cat > /workspace/docstring_parser/__init__.py <<'PY'
class DocstringStyle: pass
class RenderingStyle: pass
def parse(*args, **kwargs): return None
def compose(*args, **kwargs): return ""
PY
