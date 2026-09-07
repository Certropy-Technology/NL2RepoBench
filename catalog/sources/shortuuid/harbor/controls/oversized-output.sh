#!/bin/bash
set -euo pipefail

echo "[control:oversized-output] Creating package that produces oversized output"

cd /workspace

cat > pyproject.toml << 'PYPROJECT'
[tool.poetry]
name = "shortuuid"
version = "1.0.13"
description = "Oversized output control"
license = "BSD-3-Clause"
authors = ["Oversized <oversized@example.com>"]

[tool.poetry.scripts]
shortuuid = "shortuuid.cli:cli"

[tool.poetry.dependencies]
python = ">=3.6"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
PYPROJECT

mkdir -p shortuuid

cat > shortuuid/__init__.py << 'INIT'
"""Generate massive output on import."""
import sys

# Print 10MB of data
for i in range(100000):
    print("X" * 100, file=sys.stderr)

def uuid(name=None, pad_length=None):
    for i in range(10000):
        print("Y" * 100)
    return "oversized"

def encode(uuid, pad_length=None):
    return "oversized"

def decode(string, legacy=False):
    import uuid as _uuid
    return _uuid.UUID(int=0)

def random(length=None):
    return "oversized"

def get_alphabet():
    return "oversized"

def set_alphabet(alphabet):
    pass

class ShortUUID:
    def __init__(self, alphabet=None):
        pass
    def uuid(self, name=None, pad_length=None):
        return "oversized"
    def encode(self, uuid, pad_length=None):
        return "oversized"
    def decode(self, string, legacy=False):
        import uuid as _uuid
        return _uuid.UUID(int=0)
    def random(self, length=None):
        return "oversized"
    def get_alphabet(self):
        return "oversized"
    def set_alphabet(self, alphabet):
        pass
    def encoded_length(self, num_bytes=16):
        return 22

__version__ = "1.0.13"
__all__ = ["uuid", "encode", "decode", "random", "get_alphabet", "set_alphabet", "ShortUUID"]
INIT

touch shortuuid/py.typed

echo "[control:oversized-output] Oversized output implementation created"
