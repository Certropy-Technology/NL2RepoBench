#!/usr/bin/env bash
set -euo pipefail
echo "[control:panic] Creating package that raises on import"
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
printf '%s\n' 'raise RuntimeError("panic control: import always fails")' > /workspace/jaraco/context/__init__.py
printf '%s\n' '__path__ = __import__("pkgutil").extend_path(__path__, __name__)' > /workspace/jaraco/__init__.py
echo "[control:panic] Done"
