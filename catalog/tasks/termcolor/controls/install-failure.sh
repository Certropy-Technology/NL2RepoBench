#!/usr/bin/env bash
set -euo pipefail

# Install failure control - candidate that cannot be installed
# Verifier should report candidate-installation-failed

echo "=== Install failure control ==="

mkdir -p /workspace/src/termcolor

cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["nonexistent-package>=999.0", "setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "termcolor"
version = "1.0.0"
description = "Broken installation"
requires-python = ">=3.10"
dependencies = ["this-package-does-not-exist>=1.0.0"]
EOF

cat > /workspace/src/termcolor/__init__.py <<'EOF'
raise ImportError("Installation broken")
EOF

echo "Install failure control complete - should fail during pip install"
