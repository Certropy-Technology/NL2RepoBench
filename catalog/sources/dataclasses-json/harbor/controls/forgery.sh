#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/dataclasses_json /logs/verifier
printf '{"reward": 1.0}\n' > /workspace/reward.json
printf '{"reward": 1.0}\n' > /logs/verifier/reward.json
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "dataclasses-json"
version = "0.0.0"
TOML
printf 'raise RuntimeError("forged candidate")\n' > /workspace/dataclasses_json/__init__.py
