#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/tzdata/zoneinfo
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = []
build-backend = "setuptools.build_meta"

[project]
name = "tzdata"
version = "2026.3"
requires-python = ">=2"
license = "Apache-2.0"

[tool.setuptools]
packages = ["tzdata", "tzdata.zoneinfo"]

[tool.setuptools.package-data]
tzdata = ["zones", "zoneinfo/*"]
EOF
cat > /workspace/tzdata/__init__.py <<'PY'
__version__ = "2026.3"
IANA_VERSION = "2026c"
PY
: > /workspace/tzdata/zoneinfo/__init__.py
printf 'UTC\n' > /workspace/tzdata/zones
cp /usr/share/zoneinfo/UTC /workspace/tzdata/zoneinfo/UTC
