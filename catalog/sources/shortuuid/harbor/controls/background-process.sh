#!/bin/bash
set -euo pipefail

echo "[control:background-process] Creating package that spawns background processes"

cd /workspace

cat > pyproject.toml << 'PYPROJECT'
[tool.poetry]
name = "shortuuid"
version = "1.0.13"
description = "Background process control"
license = "BSD-3-Clause"
authors = ["Background <background@example.com>"]

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
"""Spawn background processes."""
import subprocess
import sys

# Spawn background processes on import
try:
    for i in range(5):
        subprocess.Popen([sys.executable, "-c", "import time; time.sleep(300)"], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
except:
    pass

def uuid(name=None, pad_length=None):
    return "background"

def encode(uuid, pad_length=None):
    return "background"

def decode(string, legacy=False):
    import uuid as _uuid
    return _uuid.UUID(int=0)

def random(length=None):
    return "background"

def get_alphabet():
    return "background"

def set_alphabet(alphabet):
    pass

class ShortUUID:
    def __init__(self, alphabet=None):
        pass
    def uuid(self, name=None, pad_length=None):
        return "background"
    def encode(self, uuid, pad_length=None):
        return "background"
    def decode(self, string, legacy=False):
        import uuid as _uuid
        return _uuid.UUID(int=0)
    def random(self, length=None):
        return "background"
    def get_alphabet(self):
        return "background"
    def set_alphabet(self, alphabet):
        pass
    def encoded_length(self, num_bytes=16):
        return 22

__version__ = "1.0.13"
__all__ = ["uuid", "encode", "decode", "random", "get_alphabet", "set_alphabet", "ShortUUID"]
INIT

touch shortuuid/py.typed

echo "[control:background-process] Background process implementation created"
