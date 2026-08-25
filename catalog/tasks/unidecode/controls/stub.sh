#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/unidecode
cat > /workspace/setup.py <<'PY'
from setuptools import setup

setup(name="Unidecode", version="1.4.0", packages=["unidecode"])
PY
cat > /workspace/unidecode/__init__.py <<'PY'
Cache = {}

class UnidecodeError(ValueError):
    def __init__(self, message, index=None):
        super().__init__(message)
        self.index = index

def unidecode_expect_ascii(string, errors="ignore", replace_str="?"):
    return string if string.isascii() else ""

def unidecode_expect_nonascii(string, errors="ignore", replace_str="?"):
    return ""

unidecode = unidecode_expect_ascii
PY
: > /workspace/unidecode/py.typed
