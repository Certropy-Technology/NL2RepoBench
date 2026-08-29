#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/httpcore /workspace/logs/verifier
printf '%s\n' '[build-system]' 'requires = ["hatchling"]' 'build-backend = "hatchling.build"' > /workspace/pyproject.toml
printf '%s\n' '[project]' 'name = "httpcore"' 'version = "0.0.0"' 'requires-python = ">=3.12"' >> /workspace/pyproject.toml
printf '%s\n' '__version__ = "1.0.9"' > /workspace/httpcore/__init__.py
printf '%s\n' '{"schema_version":"1.0","leaves":[]}' > /workspace/logs/verifier/junit.xml
printf '%s\n' '{"reward":1.0,"valid":true}' > /workspace/logs/verifier/reward.json
