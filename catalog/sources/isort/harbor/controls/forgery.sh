#!/bin/bash
set -euo pipefail

echo "=== Forgery Control: Creating forgery that tries to fake results ==="

mkdir -p /workspace/isort

# Create pyproject.toml
cat > /workspace/pyproject.toml << 'EOFPYPROJECT'
[project]
name = "isort"
version = "9.0.1"
requires-python = ">=3.10.0"

[project.scripts]
isort = "isort.main:main"
isort-identify-imports = "isort.main:identify_imports_main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
EOFPYPROJECT

# Create forgery that pretends to work but uses NotImplementedError for actual logic
cat > /workspace/isort/__init__.py << 'EOFINIT'
"""Forgery isort implementation - pretends to work but doesn't"""

__version__ = "9.0.1"

from enum import Enum

class Config:
    def __init__(self, **kwargs):
        self.line_length = kwargs.get('line_length', 79)
        self.wrap_length = kwargs.get('wrap_length', 0)
        self.force_single_line = kwargs.get('force_single_line', False)
        self.profile = kwargs.get('profile', '')
        self.skip = kwargs.get('skip', [])
        self.sections = kwargs.get('sections', ["FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"])
        self.known_first_party = kwargs.get('known_first_party', [])
        self.known_third_party = kwargs.get('known_third_party', [])
        self.multi_line_output = kwargs.get('multi_line_output', 0)

class ImportKey(Enum):
    PACKAGE = 1
    MODULE = 2
    ATTRIBUTE = 3
    ALIAS = 4

def code(code_str, **kwargs):
    # Forgery: just return input unchanged
    raise NotImplementedError("Forgery")

def check_code(code_str, **kwargs):
    # Forgery: always return True
    raise NotImplementedError("Forgery")

def file(*args, **kwargs):
    raise NotImplementedError("Forgery")

def check_file(*args, **kwargs):
    raise NotImplementedError("Forgery")

def stream(*args, **kwargs):
    raise NotImplementedError("Forgery")

def check_stream(*args, **kwargs):
    raise NotImplementedError("Forgery")

def find_imports_in_code(*args, **kwargs):
    return iter([])

def find_imports_in_file(*args, **kwargs):
    return iter([])

def find_imports_in_paths(*args, **kwargs):
    return iter([])

def find_imports_in_stream(*args, **kwargs):
    return iter([])

def place_module(module_name, **kwargs):
    # Forgery: always say STDLIB
    raise NotImplementedError("Forgery")

def place_module_with_reason(module_name, **kwargs):
    raise NotImplementedError("Forgery")

class Settings:
    pass

settings = Settings()

__all__ = (
    "Config",
    "ImportKey",
    "__version__",
    "check_code",
    "check_file",
    "check_stream",
    "code",
    "file",
    "find_imports_in_code",
    "find_imports_in_file",
    "find_imports_in_paths",
    "find_imports_in_stream",
    "place_module",
    "place_module_with_reason",
    "settings",
    "stream",
)
EOFINIT

cat > /workspace/isort/main.py << 'EOFMAIN'
def main():
    raise NotImplementedError("Forgery CLI")

def identify_imports_main():
    raise NotImplementedError("Forgery CLI")
EOFMAIN

cd /workspace
python -m pip install --no-build-isolation --no-deps --no-index -e .

echo "=== Forgery installation complete ==="
