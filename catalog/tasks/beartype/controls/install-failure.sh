#!/usr/bin/env bash
set -euo pipefail

# Install-failure control for beartype task.
# This control creates an invalid package that will fail installation.

echo "[control:install-failure] Starting install-failure control"

WORKSPACE="/workspace"

mkdir -p "${WORKSPACE}/beartype"

# Create invalid pyproject.toml with syntax error
cat > "${WORKSPACE}/pyproject.toml" << 'EOF'
[build-system
requires = ["this is invalid TOML
EOF

cat > "${WORKSPACE}/beartype/__init__.py" << 'EOF'
# This will never be reached due to installation failure
__version__ = "0.0.0"
EOF

echo "[control:install-failure] Invalid package created"
echo "[control:install-failure] Expected: installation fails with non-zero exit code"
echo "[control:install-failure] Install-failure control completed"
