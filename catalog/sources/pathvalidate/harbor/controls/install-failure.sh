#!/bin/bash
set -euo pipefail

mkdir -p /workspace/pathvalidate
cat > /workspace/pathvalidate/__init__.py << 'EOFPY'
# Minimal module
pass
EOFPY

# Invalid setup.py that will cause installation to fail
cat > /workspace/setup.py << 'EOFPY'
raise RuntimeError("Installation intentionally failed")
EOFPY

cat > /workspace/pyproject.toml << 'EOFPY'
[build-system]
requires = ["setuptools>=64"]
build-backend = "setuptools.build_meta"
EOFPY

cd /workspace
# This should fail
python -m pip install --no-build-isolation --no-deps --no-index -e . || true
