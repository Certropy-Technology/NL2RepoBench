#!/bin/bash
set -euo pipefail

echo "[control:oversized-output] Creating package with oversized output"

cd /workspace
rm -rf /workspace/*

cat > pyproject.toml << 'PYPROJECT'
[build-system]
build-backend = "hatchling.build"
requires = ["hatchling>=1.29"]

[project]
name = "platformdirs"
version = "4.11.3"
PYPROJECT

mkdir -p src/platformdirs

# Create __init__.py that imports normally but will produce huge output in tests
cat > src/platformdirs/__init__.py << 'INIT'
"""Package that generates oversized output."""

from __future__ import annotations

from pathlib import Path

class PlatformDirsABC:
    pass

class PlatformDirs(PlatformDirsABC):
    def __init__(self, appname=None, appauthor=None, version=None, roaming=False, multipath=False, opinion=True, ensure_exists=False, use_site_for_root=False):
        # Generate massive output when accessed
        self._huge = "X" * (10 * 1024 * 1024)  # 10MB string
        self.appname = appname
    
    @property
    def user_data_dir(self):
        print(self._huge)  # Print huge output
        return "/fake"

AppDirs = PlatformDirs

def user_data_dir(*args, **kwargs):
    pd = PlatformDirs(*args, **kwargs)
    return pd.user_data_dir

def user_config_dir(*args, **kwargs):
    return "/fake"

def user_cache_dir(*args, **kwargs):
    return "/fake"

def user_state_dir(*args, **kwargs):
    return "/fake"

def user_log_dir(*args, **kwargs):
    return "/fake"

def site_data_dir(*args, **kwargs):
    return "/fake"

def site_config_dir(*args, **kwargs):
    return "/fake"

def user_data_path(*args, **kwargs):
    return Path("/fake")

def user_config_path(*args, **kwargs):
    return Path("/fake")

def user_cache_path(*args, **kwargs):
    return Path("/fake")

__version__ = "4.11.3"
__version_info__ = (4, 11, 3)
INIT

touch src/platformdirs/py.typed

echo "[control:oversized-output] Created package that generates massive output"
