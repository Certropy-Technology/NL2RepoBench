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
description = "call timeout"
[tool.flit.module]
name = "jinja2"
TOML
printf '%s\n' 'call hang' > /workspace/README.md
cat > /workspace/jinja2/__init__.py <<'PY'
import time

class Environment:
    def from_string(self, source):
        if source == "Hello {{ name }}!":
            time.sleep(600)
        return self

    def render(self, *args, **kwargs):
        return ""

class Template:
    pass
PY
