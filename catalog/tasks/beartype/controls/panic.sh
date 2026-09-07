#!/usr/bin/env bash
set -euo pipefail

# Panic control for beartype task.
# This control creates a package that crashes on import.

echo "[control:panic] Starting panic control"

WORKSPACE="/workspace"

mkdir -p "${WORKSPACE}/beartype/door"
mkdir -p "${WORKSPACE}/beartype/vale"
mkdir -p "${WORKSPACE}/beartype/roar"
mkdir -p "${WORKSPACE}/beartype/typing"

cat > "${WORKSPACE}/pyproject.toml" << 'EOF'
[build-system]
requires = ["hatchling>=1.14.0"]
build-backend = "hatchling.build"

[project]
name = "beartype"
version = "0.22.9"
description = "Panic implementation"
requires-python = ">=3.10"
dependencies = []

[tool.hatch.build.targets.wheel]
packages = ["beartype"]
EOF

# Create package that crashes on import
cat > "${WORKSPACE}/beartype/__init__.py" << 'EOF'
"""Panic implementation that crashes on import."""
raise RuntimeError("PANIC: This package intentionally crashes on import")
EOF

touch "${WORKSPACE}/beartype/py.typed"

for module in door vale roar typing; do
    cat > "${WORKSPACE}/beartype/${module}/__init__.py" << 'EOF'
"""Panic submodule."""
raise RuntimeError("PANIC: Submodule crashes")
EOF
done

echo "[control:panic] Panic package created"
echo "[control:panic] Expected: import failures during test collection"
echo "[control:panic] Panic control completed"
