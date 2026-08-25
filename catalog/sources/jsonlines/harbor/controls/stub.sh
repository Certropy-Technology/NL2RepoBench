#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/jsonlines
cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(name="jsonlines", version="4.0.0", packages=["jsonlines"])
PY
cat > /workspace/jsonlines/__init__.py <<'PY'
class Error(Exception):
    pass


class InvalidLineError(Error, ValueError):
    pass


class Reader:
    pass


class Writer:
    pass


def open(*args, **kwargs):
    raise NotImplementedError


__all__ = ["Error", "InvalidLineError", "Reader", "Writer", "open"]
PY
