#!/bin/bash
set -euo pipefail

echo "[control:stub] Creating stub implementation with correct package structure but non-functional code"

cd /workspace

# Create pyproject.toml with setuptools backend
cat > pyproject.toml << 'PYPROJECT'
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "python-box"
version = "7.4.1"
description = "Advanced Python dictionaries with dot notation access"
readme = "README.md"
license = {text = "MIT"}
authors = [{name = "Stub", email = "stub@example.com"}]
requires-python = ">=3.9"
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
]

[project.urls]
Homepage = "https://github.com/cdgriffith/Box"
PYPROJECT

# Create README.md
cat > README.md << 'README'
# python-box stub

This is a stub implementation.
README

# Create box package
mkdir -p box

# Create __init__.py with stub classes that raise NotImplementedError
cat > box/__init__.py << 'INIT'
"""Stub implementation of python-box."""

class BoxError(Exception):
    """Stub BoxError."""
    pass

class BoxKeyError(KeyError, BoxError):
    """Stub BoxKeyError."""
    pass

class Box(dict):
    """Stub Box class."""
    
    def __init__(self, *args, **kwargs):
        # Allow construction but methods will fail
        super().__init__()
    
    def __getattr__(self, item):
        raise NotImplementedError("Stub implementation")
    
    def __setattr__(self, key, value):
        raise NotImplementedError("Stub implementation")
    
    def __delattr__(self, item):
        raise NotImplementedError("Stub implementation")
    
    def to_dict(self):
        raise NotImplementedError("Stub implementation")
    
    def to_json(self):
        raise NotImplementedError("Stub implementation")
    
    @classmethod
    def from_json(cls, json_string):
        raise NotImplementedError("Stub implementation")
    
    def merge_update(self, *args, **kwargs):
        raise NotImplementedError("Stub implementation")
    
    def copy(self):
        raise NotImplementedError("Stub implementation")

class BoxList(list):
    """Stub BoxList class."""
    
    def __init__(self, *args, **kwargs):
        super().__init__()
    
    def __getitem__(self, item):
        raise NotImplementedError("Stub implementation")
    
    def append(self, item):
        raise NotImplementedError("Stub implementation")
    
    def extend(self, items):
        raise NotImplementedError("Stub implementation")
    
    def insert(self, index, item):
        raise NotImplementedError("Stub implementation")

class DDBox(Box):
    """Stub DDBox class."""
    pass

def box_from_string(string):
    """Stub box_from_string function."""
    raise NotImplementedError("Stub implementation")

__version__ = "7.4.1"
__all__ = ["Box", "BoxList", "DDBox", "BoxError", "BoxKeyError", "box_from_string"]
INIT

echo "[control:stub] Stub implementation created"
echo "[control:stub] Package structure is correct but all methods raise NotImplementedError"
