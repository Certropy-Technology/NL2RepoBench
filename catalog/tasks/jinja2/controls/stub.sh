#!/usr/bin/env bash
set -euo pipefail
cd /tmp
rm -rf /workspace
mkdir -p /workspace/jinja2
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["flit_core<4"]
build-backend = "flit_core.buildapi"
[project]
name = "Jinja2"
version = "3.2.0.dev"
description = "stub"
dependencies = ["MarkupSafe>=3.0"]
[tool.flit.module]
name = "jinja2"
TOML
printf '%s\n' 'stub' > /workspace/README.md
cat > /workspace/jinja2/__init__.py <<'PY'
class Environment:
    def __init__(self, *args, **kwargs): pass
class Template: pass
PY
