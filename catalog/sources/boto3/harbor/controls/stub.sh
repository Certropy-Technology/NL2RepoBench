#!/usr/bin/env bash
set -euo pipefail

root=/workspace
rm -rf "$root"/* "$root"/.[!.]* "$root"/..?*
mkdir -p "$root/boto3"
cat > "$root/setup.py" <<'PY'
from setuptools import setup

setup(name="boto3", version="1.43.78", packages=["boto3"])
PY
cat > "$root/boto3/__init__.py" <<'PY'
__version__ = "1.43.78"

class Session:
    def __init__(self, *args, **kwargs):
        self.region_name = kwargs.get("region_name")

    def client(self, *args, **kwargs):
        raise NotImplementedError

    def resource(self, *args, **kwargs):
        raise NotImplementedError

def setup_default_session(**kwargs):
    global DEFAULT_SESSION
    DEFAULT_SESSION = Session(**kwargs)

def client(*args, **kwargs):
    raise NotImplementedError

def resource(*args, **kwargs):
    raise NotImplementedError

DEFAULT_SESSION = None
PY
