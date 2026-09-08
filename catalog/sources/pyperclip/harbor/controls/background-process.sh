#!/bin/bash
set -euo pipefail
echo "[control:background-process] Creating package that spawns background processes"
cd /workspace
cat > pyproject.toml << 'PYPROJECT'
[build-system]
requires = ["setuptools>=70"]
build-backend = "setuptools.build_meta"

[project]
name = "pyperclip"
version = "0.0.0"
description = "Background process control"

[tool.setuptools]
packages = ["pyperclip"]
PYPROJECT
mkdir -p pyperclip
cat > pyperclip/__init__.py << 'INIT'
import subprocess
import sys
try:
    for _ in range(5):
        subprocess.Popen([sys.executable, "-c", "import time; time.sleep(300)"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except Exception:
    pass
INIT
echo "[control:background-process] Done"
