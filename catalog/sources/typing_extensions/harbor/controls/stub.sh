#!/usr/bin/env bash
set -euo pipefail

cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["flit_core >=3.11,<4"]
build-backend = "flit_core.buildapi"

[project]
name = "typing_extensions"
version = "4.14.1"
description = "Backported and experimental type hints"
TOML
cat > /workspace/typing_extensions.py <<'PY'
"""Installable low-behavior control for typing_extensions."""

import typing

__all__ = ["Any", "get_args", "get_origin"]
Any = typing.Any
get_args = typing.get_args
get_origin = typing.get_origin
PY
