#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/tzlocal
cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(name="tzlocal", version="5.4.5.dev0", packages=["tzlocal"])
PY
cat > /workspace/tzlocal/__init__.py <<'PY'
from datetime import timezone

__all__ = ["get_localzone", "get_localzone_name", "reload_localzone", "assert_tz_offset"]

def get_localzone():
    return timezone.utc

def get_localzone_name():
    return "UTC"

def reload_localzone():
    return timezone.utc

def assert_tz_offset(tz, error=True):
    return None
PY
