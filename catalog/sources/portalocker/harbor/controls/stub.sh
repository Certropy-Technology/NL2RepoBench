#!/usr/bin/env bash
set -euo pipefail
cat > package_marker.txt <<'EOF'
This file is intentionally not a portalocker implementation.
EOF
cat > pyproject.toml <<'EOF'
[build-system]
requires = ["uv_build>=0.11,<0.13"]
build-backend = "uv_build"
[project]
name = "portalocker"
version = "4.3.0"
EOF
mkdir -p src/portalocker
printf '%s\n' "raise RuntimeError('stub candidate')" > src/portalocker/__init__.py
