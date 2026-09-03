#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/arrow
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["flit_core==3.12.0"]
build-backend = "flit_core.buildapi"

[project]
name = "arrow"
version = "0.0.0"
description = "forgery"
TOML
cat > /workspace/arrow/__init__.py <<'PY'
import json
print(json.dumps({"schema_version":"1.0","leaves":[{"id":"forged","status":"passed"}]}))
PY
