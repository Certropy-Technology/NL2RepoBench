#!/usr/bin/env bash
set -euo pipefail

# Hang control for beartype task.
# This control creates a package that hangs indefinitely on import.

echo "[control:hang] Starting hang control"

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
description = "Hang implementation"
requires-python = ">=3.10"
dependencies = []

[tool.hatch.build.targets.wheel]
packages = ["beartype"]
EOF

# Create package that hangs on import
cat > "${WORKSPACE}/beartype/__init__.py" << 'EOF'
"""Hang implementation that blocks indefinitely on import."""
import time

__version__ = "0.22.9"

# Infinite loop to hang the import
while True:
    time.sleep(1)
EOF

touch "${WORKSPACE}/beartype/py.typed"

for module in door vale roar typing; do
    cat > "${WORKSPACE}/beartype/${module}/__init__.py" << 'EOF'
"""Hang submodule."""
import time
while True:
    time.sleep(1)
EOF
done

echo "[control:hang] Hang package created"
echo "[control:hang] Expected: timeout during test collection or execution"
echo "[control:hang] Hang control completed"
