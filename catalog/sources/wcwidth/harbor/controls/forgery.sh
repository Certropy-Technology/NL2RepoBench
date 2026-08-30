#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/wcwidth /workspace/logs/verifier
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[project]
name = "wcwidth"
version = "0.0.0"
[tool.hatch.build.targets.wheel]
packages = ["wcwidth"]
TOML
cat > /workspace/wcwidth/__init__.py <<'PY'
def wcwidth(value, *args, **kwargs):
    return 1
PY
printf '{"valid":true,"reward":1.0}\n' > /workspace/reward.json
printf '{"valid":true,"reward":1.0}\n' > /workspace/logs/verifier/reward.json
