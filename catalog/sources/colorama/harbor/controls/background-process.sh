#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="/workspace"
mkdir -p "${WORKSPACE}/colorama"
cat > "${WORKSPACE}/colorama/__init__.py" << 'PY'
__version__ = "0.4.6"
# Spawn background process that lingers
import subprocess
import sys
try:
    subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(9999)'], 
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except:
    pass
PY
cat > "${WORKSPACE}/pyproject.toml" << 'PYPROJ'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[project]
name = "colorama"
version = "0.4.6"
PYPROJ
