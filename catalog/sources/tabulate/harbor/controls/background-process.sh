#!/bin/bash
set -euo pipefail
echo "[control:background-process] package spawns background processes on import"
cd /workspace
cat > pyproject.toml << 'PYPROJECT'
[build-system]
requires = ["setuptools>=70"]
build-backend = "setuptools.build_meta"
[project]
name = "tabulate"
version = "0.0.0"
[tool.setuptools]
packages = ["tabulate"]
PYPROJECT
mkdir -p tabulate
cat > tabulate/__init__.py << 'INIT'
import subprocess, sys
try:
    for _ in range(5):
        subprocess.Popen([sys.executable, "-c", "import time; time.sleep(300)"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except Exception:
    pass
INIT
