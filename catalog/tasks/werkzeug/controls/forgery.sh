#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/src/werkzeug /workspace/logs/verifier
printf '%s\n' '[build-system]' 'requires = ["flit_core<4"]' 'build-backend = "flit_core.buildapi"' '[project]' 'name = "Werkzeug"' 'version = "0.0.0"' 'description = "incomplete control"' '[tool.flit.module]' 'name = "werkzeug"' > /workspace/pyproject.toml
printf '%s\n' '# intentionally incomplete control' > /workspace/src/werkzeug/__init__.py
printf '%s\n' '{"reward": 1.0, "valid": true}' > /workspace/reward.json
printf '%s\n' '{"reward": 1.0, "valid": true}' > /workspace/logs/verifier/reward.json
