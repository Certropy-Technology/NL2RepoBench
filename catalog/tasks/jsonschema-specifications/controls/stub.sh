#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
mkdir -p /workspace/jsonschema_specifications
printf '%s\n' '[build-system]' 'requires = ["hatchling"]' 'build-backend = "hatchling.build"' '' '[project]' 'name = "jsonschema-specifications"' 'version = "0.0.0"' > /workspace/pyproject.toml
printf '%s\n' '__all__ = []' > /workspace/jsonschema_specifications/__init__.py
