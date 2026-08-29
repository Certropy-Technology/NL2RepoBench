#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
mkdir -p /workspace/regex
printf '%s\n' '[build-system]' 'requires = ["setuptools"]' 'build-backend = "setuptools.build_meta"' > /workspace/pyproject.toml
printf '%s\n' 'from setuptools import setup' 'setup(name="regex", version="0.0.0", packages=["regex"])' > /workspace/setup.py
printf '%s\n' '__version__ = "0.0.0"' > /workspace/regex/__init__.py
