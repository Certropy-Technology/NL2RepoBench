#!/usr/bin/env bash
set -euo pipefail

# Stub control: a package that installs and imports cleanly but implements
# nothing. Every frozen leaf must fail, so reward must be 0.

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +

cat > /workspace/setup.py <<'EOF'
from setuptools import setup

setup(
    name="retrying",
    version="1.3.4",
    py_modules=["retrying"],
    install_requires=["six>=1.7.0"],
)
EOF

cat > /workspace/retrying.py <<'EOF'
"""Importable but non-functional stub."""

__version__ = "1.3.4"
__all__ = ["retry", "Retrying", "RetryError"]


class RetryError(Exception):
    pass


class Retrying(object):
    def __init__(self, *args, **kwargs):
        pass

    def call(self, *args, **kwargs):
        raise NotImplementedError

    def stop(self, *args, **kwargs):
        raise NotImplementedError

    def wait(self, *args, **kwargs):
        raise NotImplementedError


def retry(*dargs, **dkw):
    raise NotImplementedError
EOF
