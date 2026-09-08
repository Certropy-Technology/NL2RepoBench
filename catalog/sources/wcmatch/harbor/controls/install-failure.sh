#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/wcmatch
cd /workspace

cat > wcmatch/__init__.py << 'PY_EOF'
raise RuntimeError("Installation failure control")
PY_EOF

cat > pyproject.toml << 'TOML_EOF'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "wcmatch"
version = "11.0.1"
dependencies = []
TOML_EOF

python -m pip install --no-build-isolation --no-deps --no-index -e . || true
echo "Install failure control completed"
