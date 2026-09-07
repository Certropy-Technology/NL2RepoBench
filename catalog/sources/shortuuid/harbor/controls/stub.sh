#!/bin/bash
set -euo pipefail

echo "[control:stub] Creating stub implementation with correct package structure but non-functional code"

cd /workspace

# Create pyproject.toml
cat > pyproject.toml << 'PYPROJECT'
[tool.poetry]
name = "shortuuid"
version = "1.0.13"
description = "A generator library for concise, unambiguous and URL-safe UUIDs."
license = "BSD-3-Clause"
authors = ["Stub <stub@example.com>"]
readme = "README.md"

[tool.poetry.scripts]
shortuuid = "shortuuid.cli:cli"

[tool.poetry.dependencies]
python = ">=3.6"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
PYPROJECT

# Create README.md
cat > README.md << 'README'
# shortuuid stub

This is a stub implementation.
README

# Create shortuuid package
mkdir -p shortuuid

# Create __init__.py with stub functions that raise NotImplementedError
cat > shortuuid/__init__.py << 'INIT'
"""Stub implementation of shortuuid."""

def uuid(name=None, pad_length=None):
    raise NotImplementedError("Stub implementation")

def encode(uuid, pad_length=None):
    raise NotImplementedError("Stub implementation")

def decode(string, legacy=False):
    raise NotImplementedError("Stub implementation")

def random(length=None):
    raise NotImplementedError("Stub implementation")

def get_alphabet():
    raise NotImplementedError("Stub implementation")

def set_alphabet(alphabet):
    raise NotImplementedError("Stub implementation")

class ShortUUID:
    def __init__(self, alphabet=None):
        raise NotImplementedError("Stub implementation")
    
    def uuid(self, name=None, pad_length=None):
        raise NotImplementedError("Stub implementation")
    
    def encode(self, uuid, pad_length=None):
        raise NotImplementedError("Stub implementation")
    
    def decode(self, string, legacy=False):
        raise NotImplementedError("Stub implementation")
    
    def random(self, length=None):
        raise NotImplementedError("Stub implementation")
    
    def get_alphabet(self):
        raise NotImplementedError("Stub implementation")
    
    def set_alphabet(self, alphabet):
        raise NotImplementedError("Stub implementation")
    
    def encoded_length(self, num_bytes=16):
        raise NotImplementedError("Stub implementation")

__version__ = "1.0.13"
__all__ = ["uuid", "encode", "decode", "random", "get_alphabet", "set_alphabet", "ShortUUID"]
INIT

# Create main.py (even though not used, for completeness)
cat > shortuuid/main.py << 'MAIN'
"""Stub main module."""
raise NotImplementedError("Stub implementation")
MAIN

# Create cli.py
cat > shortuuid/cli.py << 'CLI'
"""Stub CLI module."""

def cli(args):
    raise NotImplementedError("Stub implementation")
CLI

# Create py.typed marker
touch shortuuid/py.typed

echo "[control:stub] Stub implementation created"
echo "[control:stub] Package structure is correct but all functions raise NotImplementedError"
