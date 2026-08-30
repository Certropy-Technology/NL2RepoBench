#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/tomli
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["flit_core>=3.12,<4"]
build-backend = "flit_core.buildapi"
[project]
name = "tomli"
version = "2.4.1"
description = "call timeout control"
requires-python = ">=3.8"
[tool.flit.module]
name = "tomli"
EOF
cat > /workspace/src/tomli/__init__.py <<'EOF'
import time
__version__ = "2.4.1"
def loads(text, *, parse_float=float):
    time.sleep(600)
def load(fp, *, parse_float=float):
    time.sleep(600)
class TOMLDecodeError(ValueError):
    pass
EOF
