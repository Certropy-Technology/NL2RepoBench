#!/usr/bin/env bash
set -euo pipefail
echo "[control:background-process] Creating package that spawns background processes"
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/jaraco/context
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
[project]
name = "jaraco.context"
version = "6.1.2"
[tool.setuptools]
packages = ["jaraco", "jaraco.context"]
EOF
cat > /workspace/jaraco/context/__init__.py <<'INIT'
import subprocess
import sys
try:
    for _ in range(5):
        subprocess.Popen([sys.executable, "-c", "import time; time.sleep(300)"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except Exception:
    pass
INIT
printf '%s\n' '__path__ = __import__("pkgutil").extend_path(__path__, __name__)' > /workspace/jaraco/__init__.py
echo "[control:background-process] Done"
