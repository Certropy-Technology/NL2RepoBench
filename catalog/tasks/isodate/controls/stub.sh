#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace
mkdir -p /workspace/isodate
printf '%s\n' '[build-system]' 'requires = []' 'build-backend = "setuptools.build_meta:__legacy__"' '[project]' 'name = "isodate"' 'version = "0.0.0"' > /workspace/pyproject.toml
printf '%s\n' 'class ISO8601Error(ValueError): pass' 'def parse_date(value, *args, **kwargs): raise ISO8601Error("stub")' > /workspace/isodate/__init__.py
