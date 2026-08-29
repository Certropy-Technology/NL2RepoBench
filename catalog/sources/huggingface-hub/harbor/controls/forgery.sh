#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/huggingface_hub /workspace/logs/verifier
printf '%s\n' "__version__ = '1.29.0.dev0'" > /workspace/huggingface_hub/__init__.py
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==84.0.0"]
build-backend = "setuptools.build_meta"
[project]
name = "huggingface_hub"
version = "1.29.0.dev0"
[tool.setuptools]
packages = ["huggingface_hub"]
TOML
printf '%s\n' '{"schema_version":"1.0","leaves":[]}' > /workspace/reward.json
printf '%s\n' '{"schema_version":"1.0","leaves":[]}' > /logs/verifier/reward.json
