#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/charset_normalizer
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"
[project]
name = "charset-normalizer"
version = "3.5.1"
TOML
cat > /workspace/charset_normalizer/__init__.py <<'PY'
__version__ = "3.5.1"
VERSION = ["3", "5", "1"]
__all__ = []
PY
