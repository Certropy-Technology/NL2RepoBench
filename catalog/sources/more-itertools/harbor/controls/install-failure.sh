#!/bin/bash
set -euo pipefail

echo "[control:install-failure] Creating package with invalid pyproject.toml"

cd /workspace

# Create invalid pyproject.toml (broken TOML syntax)
cat > pyproject.toml << 'PYPROJECT'
[project]
name = "more-itertools"
version = "11.1.0"
description = "More routines for operating on iterables, beyond itertools"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}

[build-system]
requires = ["flit_core >=3.2,<4"]
build-backend = "flit_core.buildapi"
INVALID TOML LINE WITHOUT PROPER SYNTAX
PYPROJECT

cat > README.md << 'README'
# more-itertools install-failure
README

mkdir -p more_itertools
cat > more_itertools/__init__.py << 'INIT'
__version__ = "11.1.0"
INIT

echo "[control:install-failure] Created package with invalid pyproject.toml - should fail to install"
