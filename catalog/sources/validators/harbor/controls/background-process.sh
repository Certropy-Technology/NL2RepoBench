#!/usr/bin/env bash
set -euo pipefail

cd /workspace

mkdir -p src/validators

cat > pyproject.toml << 'PYPROJECT'
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "validators"
version = "0.35.0"
requires-python = ">=3.9"
dependencies = []

[tool.setuptools.packages.find]
where = ["src"]
include = ["validators*"]
PYPROJECT

# Create package that spawns background processes on import
cat > src/validators/__init__.py << 'INIT'
"""Background process package - spawns processes on import."""
import subprocess
import sys

for i in range(5):
    subprocess.Popen([sys.executable, "-c", "import time; time.sleep(300)"])

__version__ = "0.35.0"
INIT

# Install background process package
python -m pip install --no-build-isolation --no-deps --no-index -e .
echo "Background process package installed"
