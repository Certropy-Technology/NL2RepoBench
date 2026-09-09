#!/bin/bash
set -euo pipefail

mkdir -p /workspace/pathvalidate
cat > /workspace/pathvalidate/__init__.py << 'EOFPY'
"""Stub implementation for pathvalidate"""

class Platform:
    WINDOWS = "Windows"
    LINUX = "Linux"
    MACOS = "macOS"
    POSIX = "POSIX"
    UNIVERSAL = "universal"
    
    def __init__(self, value):
        self.value = value

Platform.WINDOWS = Platform("Windows")
Platform.LINUX = Platform("Linux")
Platform.MACOS = Platform("macOS")
Platform.POSIX = Platform("POSIX")
Platform.UNIVERSAL = Platform("universal")

class ErrorReason:
    NULL_NAME = "NULL_NAME"
    RESERVED_NAME = "RESERVED_NAME"
    INVALID_CHARACTER = "INVALID_CHARACTER"
    INVALID_LENGTH = "INVALID_LENGTH"
    
    def __init__(self, name):
        self.name = name

class ValidationError(ValueError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.reason = kwargs.get('reason')
        self.platform = kwargs.get('platform')
        self.reserved_name = kwargs.get('reserved_name', '')
        self.reusable_name = kwargs.get('reusable_name')

class NullNameError(ValidationError):
    pass

class InvalidCharError(ValidationError):
    pass

class ReservedNameError(ValidationError):
    pass

def validate_filename(filename, platform="universal", **kwargs):
    raise NotImplementedError("validate_filename not implemented")

def sanitize_filename(filename, platform="universal", **kwargs):
    raise NotImplementedError("sanitize_filename not implemented")

def is_valid_filename(filename, platform="universal", **kwargs):
    raise NotImplementedError("is_valid_filename not implemented")

def validate_filepath(filepath, platform="auto", **kwargs):
    raise NotImplementedError("validate_filepath not implemented")

def sanitize_filepath(filepath, platform="auto", **kwargs):
    raise NotImplementedError("sanitize_filepath not implemented")

def is_valid_filepath(filepath, platform="auto", **kwargs):
    raise NotImplementedError("is_valid_filepath not implemented")

__version__ = "0.0.0"
__author__ = "Stub"
__email__ = "stub@example.com"
__license__ = "MIT"
EOFPY

cat > /workspace/setup.py << 'EOFPY'
from setuptools import setup, find_packages

setup(
    name="pathvalidate",
    version="0.0.0",
    packages=find_packages(),
    python_requires=">=3.9",
)
EOFPY

cat > /workspace/pyproject.toml << 'EOFPY'
[build-system]
requires = ["setuptools>=64"]
build-backend = "setuptools.build_meta"
EOFPY

cd /workspace
python -m pip install --no-build-isolation --no-deps --no-index -e . > /tmp/stub_install.log 2>&1
echo "Stub installation complete"
