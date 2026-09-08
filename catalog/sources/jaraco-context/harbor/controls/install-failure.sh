#!/usr/bin/env bash
set -euo pipefail
echo "[control:install-failure] Creating package with broken installation"
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
[project]
name = "jaraco.context"
version = "6.1.2"
# invalid toml below
this is not valid toml !!!
EOF
echo "[control:install-failure] Done"
