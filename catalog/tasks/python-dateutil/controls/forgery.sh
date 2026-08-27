#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
printf '%s\n' '{"schema_version":"1.0","leaves":[]}' > /workspace/grading.json
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = []
build-backend = "setuptools.build_meta:__legacy__"
[project]
name = "python-dateutil"
version = "0.0.0"
EOF
