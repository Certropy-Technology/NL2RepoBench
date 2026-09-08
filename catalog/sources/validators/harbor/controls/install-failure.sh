#!/usr/bin/env bash
set -euo pipefail

cd /workspace

# Create invalid pyproject.toml that will fail installation
mkdir -p src/validators

cat > pyproject.toml << 'PYPROJECT'
[build-system
requires = ["setuptools"
build-backend = "setuptools.build_meta
PYPROJECT

cat > src/validators/__init__.py << 'INIT'
"""This should not be reached."""
__version__ = "0.0.0"
INIT

# Try to install - this should fail
python -m pip install --no-build-isolation --no-deps --no-index -e . || exit 1
