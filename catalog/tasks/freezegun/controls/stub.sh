#!/usr/bin/env bash
set -euo pipefail

cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(
    name="freezegun",
    version="1.5.5",
    packages=["freezegun"],
    install_requires=["python-dateutil>=2.7"],
)
PY
mkdir -p /workspace/freezegun
cat > /workspace/freezegun/__init__.py <<'PY'
"""Installable low-behavior control for freezegun."""

__version__ = "1.5.5"
__all__ = ["freeze_time"]


def freeze_time(*args, **kwargs):
    raise NotImplementedError("control stub")
PY
