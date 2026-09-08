#!/bin/bash
# Install failure control - invalid package that cannot be installed
set -euo pipefail
echo "=== Install failure control: Creating invalid package ==="

cd /workspace

# Create invalid pyproject.toml
cat > pyproject.toml << 'PYPROJECT'
[build-system]
requires = ["nonexistent-build-backend>=999"]
build-backend = "nonexistent.backend"

[project]
name = "tomli_w"
PYPROJECT

echo "Invalid package created"
exit 0
