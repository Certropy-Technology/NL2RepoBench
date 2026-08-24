#!/usr/bin/env bash
# Stub control: a minimally-importable but non-functional `records` package.
# The candidate install must succeed so the verifier reaches its probes, but
# every behavioural leaf must fail.
set -euo pipefail

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true

cat > /workspace/setup.py <<'EOF'
from setuptools import setup

setup(
    name="records",
    version="0.6.0",
    description="SQL for Humans",
    py_modules=["records"],
    license="ISC",
    zip_safe=False,
)
EOF

cat > /workspace/records.py <<'EOF'
"""Importable stub with no working behaviour."""

__version__ = "0.6.0"


def isexception(obj):
    raise NotImplementedError


class Record(object):
    def __init__(self, keys, values):
        raise NotImplementedError


class RecordCollection(object):
    def __init__(self, rows):
        raise NotImplementedError


class Connection(object):
    def __init__(self, connection, close_with_result=False):
        raise NotImplementedError


class Database(object):
    def __init__(self, db_url=None, **kwargs):
        raise NotImplementedError


def cli():
    raise NotImplementedError
EOF
