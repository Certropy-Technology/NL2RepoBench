#!/bin/bash
set -euo pipefail

echo "[control:background-process] Creating package that spawns background processes"

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

# Create __init__.py that spawns background process on import
cat > src/platformdirs/__init__.py << 'INIT'
"""Package that spawns background processes."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# Spawn background sleep process on import
try:
    subprocess.Popen([sys.executable, "-c", "import time; time.sleep(300)"])
except Exception:
    pass

class PlatformDirsABC:
    pass

class PlatformDirs(PlatformDirsABC):
    def __init__(self, appname=None, appauthor=None, version=None, roaming=False, multipath=False, opinion=True, ensure_exists=False, use_site_for_root=False):
        self.appname = appname
    
    @property
    def user_data_dir(self):
        return "/fake"

AppDirs = PlatformDirs

def user_data_dir(*args, **kwargs):
    return "/fake"

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

echo "[control:background-process] Created package that spawns background process"
