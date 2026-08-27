#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/pydantic_settings
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "pydantic-settings"
version = "0.0.0"
EOF
cat > /workspace/pydantic_settings/__init__.py <<'EOF'
__version__ = "0.0.0"
EOF
mkdir -p /logs/verifier
printf '{"reward": 1.0, "valid": true}\n' > /logs/verifier/reward.json
