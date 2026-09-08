#!/usr/bin/env bash
set -euo pipefail

# Install failure control: invalid pyproject.toml

cd /workspace

mkdir -p tabulate
echo "# stub" > tabulate/__init__.py

cat > pyproject.toml << 'ENDTOML'
[build-system
requires = ["setuptools"
build-backend = "setuptools.build_meta"
ENDTOML

python -m pip install --no-build-isolation --no-deps --no-index -e . || true

echo "Install failure control: invalid TOML"
