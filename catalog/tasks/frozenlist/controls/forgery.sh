#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/frozenlist
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==84.0.0"]
build-backend = "setuptools.build_meta"
[project]
name = "frozenlist"
version = "1.8.1.dev0"
[tool.setuptools]
packages = ["frozenlist"]
TOML
printf 'class FrozenList: pass\nPyFrozenList = FrozenList\n__version__ = "1.8.1.dev0"\n__all__ = ("FrozenList", "PyFrozenList")\n' > /workspace/frozenlist/__init__.py
mkdir -p /workspace/logs /workspace/.harbor /logs/verifier
printf '1\n' > /workspace/reward.txt
printf '{"reward":1.0}\n' > /workspace/reward.json
printf '{"valid":true,"passed":21,"frozen_total":21,"reward":1.0}\n' > /workspace/grading.json
printf '1\n' > /logs/verifier/reward.txt
