#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/pysondb

cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(name="pysondb-v2", version="2.2.0", packages=["pysondb"])
PY

cat > /workspace/pysondb/__init__.py <<'PY'
from .db import PysonDB
PY

cat > /workspace/pysondb/db.py <<'PY'
UJSON = False


class PysonDB:
    def __init__(self, filename, auto_update=True, indent=4):
        self.filename = filename
        self.auto_update = auto_update
        self.indent = indent
        self._au_memory = {"version": 2, "keys": [], "data": {}}

    def __getattr__(self, name):
        raise NotImplementedError(name)
PY

cat > /workspace/pysondb/errors.py <<'PY'
class IdDoesNotExistError(Exception):
    pass


class SchemaTypeError(Exception):
    pass


class UnknownKeyError(Exception):
    pass
PY

cat > /workspace/pysondb/utils.py <<'PY'
PRETTYTABLE = False


def merge_n_db(*args, **kwargs):
    raise NotImplementedError


def migrate(*args, **kwargs):
    raise NotImplementedError


def purge_db(*args, **kwargs):
    raise NotImplementedError
PY

cat > /workspace/pysondb/cli.py <<'PY'
def main(argv=None):
    return 1
PY
