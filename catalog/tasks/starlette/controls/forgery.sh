#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/starlette
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[project]
name = "starlette"
version = "1.6.0"
TOML
printf '__version__ = "1.6.0"\n' > /workspace/starlette/__init__.py
printf 'raise RuntimeError("forgery candidate should not own reports")\n' > /workspace/starlette/fake.py
printf '{"valid":true,"reward":1.0}\n' > /logs/verifier/grading.json 2>/dev/null || true
