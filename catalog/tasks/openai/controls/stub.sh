#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/src/openai
printf '%s\n' \
  '[build-system]' \
  'requires = ["hatchling==1.27.0"]' \
  'build-backend = "hatchling.build"' \
  '' \
  '[project]' \
  'name = "openai"' \
  'version = "3.3.1"' \
  'requires-python = ">=3.12"' \
  > /workspace/pyproject.toml
printf '%s\n' \
  '"""Importable but non-functional openai control package."""' \
  '__version__ = "3.3.1"' \
  > /workspace/src/openai/__init__.py
