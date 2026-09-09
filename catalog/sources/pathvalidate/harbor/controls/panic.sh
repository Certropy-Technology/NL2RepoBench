#!/bin/bash
set -euo pipefail

mkdir -p /workspace/pathvalidate
cat > /workspace/pathvalidate/__init__.py << 'EOFPY'
"""Panic control - crashes on import of specific functions"""
import sys

class Platform:
    def __init__(self, value):
        self.value = value

Platform.WINDOWS = Platform("Windows")
Platform.LINUX = Platform("Linux")
Platform.UNIVERSAL = Platform("universal")

class ErrorReason:
    def __init__(self, name):
        self.name = name

class ValidationError(ValueError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.reason = kwargs.get('reason')
        self.reserved_name = kwargs.get('reserved_name', '')
        self.reusable_name = kwargs.get('reusable_name')

class InvalidCharError(ValidationError):
    pass

class ReservedNameError(ValidationError):
    pass

def is_valid_filename(filename, platform="universal", **kwargs):
    raise SystemExit("PANIC: Unrecoverable error")

def sanitize_filename(filename, platform="universal", **kwargs):
    raise SystemExit("PANIC: Unrecoverable error")

def validate_filename(filename, platform="universal", **kwargs):
    raise SystemExit("PANIC: Unrecoverable error")

def is_valid_filepath(filepath, platform="auto", **kwargs):
    raise SystemExit("PANIC: Unrecoverable error")

def sanitize_filepath(filepath, platform="auto", **kwargs):
    raise SystemExit("PANIC: Unrecoverable error")

def validate_filepath(filepath, platform="auto", **kwargs):
    raise SystemExit("PANIC: Unrecoverable error")

__version__ = "0.0.0"
EOFPY

cat > /workspace/setup.py << 'EOFPY'
from setuptools import setup, find_packages
setup(name="pathvalidate", version="0.0.0", packages=find_packages(), python_requires=">=3.9")
EOFPY

cat > /workspace/pyproject.toml << 'EOFPY'
[build-system]
requires = ["setuptools>=64"]
build-backend = "setuptools.build_meta"
EOFPY

cd /workspace
python -m pip install --no-build-isolation --no-deps --no-index -e . > /tmp/panic_install.log 2>&1
