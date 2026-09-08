#!/bin/bash
set -euo pipefail

echo "[control:stub] Creating stub implementation with correct package structure but non-functional code"

cd /workspace
rm -rf /workspace/*

# Create pyproject.toml
cat > pyproject.toml << 'PYPROJECT'
[build-system]
build-backend = "hatchling.build"
requires = ["hatchling>=1.29"]

[project]
name = "platformdirs"
version = "4.11.3"
description = "Stub implementation"
requires-python = ">=3.10"
PYPROJECT

# Create src/platformdirs package
mkdir -p src/platformdirs

# Create __init__.py with stub functions that raise NotImplementedError
cat > src/platformdirs/__init__.py << 'INIT'
"""Stub implementation of platformdirs."""

from __future__ import annotations

from pathlib import Path

class PlatformDirsABC:
    def __init__(self, appname=None, appauthor=None, version=None, roaming=False, multipath=False, opinion=True, ensure_exists=False, use_site_for_root=False):
        raise NotImplementedError("Stub implementation")

class PlatformDirs(PlatformDirsABC):
    pass

# Alias
AppDirs = PlatformDirs

# Stub convenience functions
def user_data_dir(appname=None, appauthor=None, version=None, roaming=False, ensure_exists=False):
    raise NotImplementedError("Stub implementation")

def user_config_dir(appname=None, appauthor=None, version=None, roaming=False, ensure_exists=False):
    raise NotImplementedError("Stub implementation")

def user_cache_dir(appname=None, appauthor=None, version=None, opinion=True, ensure_exists=False):
    raise NotImplementedError("Stub implementation")

def user_state_dir(appname=None, appauthor=None, version=None, roaming=False, ensure_exists=False):
    raise NotImplementedError("Stub implementation")

def user_log_dir(appname=None, appauthor=None, version=None, opinion=True, ensure_exists=False):
    raise NotImplementedError("Stub implementation")

def site_data_dir(appname=None, appauthor=None, version=None, multipath=False, ensure_exists=False):
    raise NotImplementedError("Stub implementation")

def site_config_dir(appname=None, appauthor=None, version=None, multipath=False, ensure_exists=False):
    raise NotImplementedError("Stub implementation")

def user_data_path(appname=None, appauthor=None, version=None, roaming=False, ensure_exists=False):
    raise NotImplementedError("Stub implementation")

def user_config_path(appname=None, appauthor=None, version=None, roaming=False, ensure_exists=False):
    raise NotImplementedError("Stub implementation")

def user_cache_path(appname=None, appauthor=None, version=None, opinion=True, ensure_exists=False):
    raise NotImplementedError("Stub implementation")

__version__ = "4.11.3"
__version_info__ = (4, 11, 3)

__all__ = [
    "PlatformDirs",
    "PlatformDirsABC",
    "AppDirs",
    "user_data_dir",
    "user_config_dir",
    "user_cache_dir",
    "user_state_dir",
    "user_log_dir",
    "site_data_dir",
    "site_config_dir",
    "user_data_path",
    "user_config_path",
    "user_cache_path",
    "__version__",
    "__version_info__",
]
INIT

# Create __main__.py stub
cat > src/platformdirs/__main__.py << 'MAIN'
"""Stub main module."""
raise NotImplementedError("Stub implementation")
MAIN

# Create py.typed marker
touch src/platformdirs/py.typed

echo "[control:stub] Stub implementation created"
echo "[control:stub] Package structure is correct but all functions raise NotImplementedError"
