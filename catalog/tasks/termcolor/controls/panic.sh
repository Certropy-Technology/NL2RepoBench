#!/usr/bin/env bash
set -euo pipefail

# Panic control - candidate that crashes on import
# Verifier should handle gracefully

echo "=== Panic control ==="

mkdir -p /workspace/src/termcolor

cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools>=70", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "termcolor"
version = "1.0.0"
description = "Panic implementation"
requires-python = ">=3.10"
dependencies = []

[tool.setuptools.packages.find]
where = ["src"]
EOF

cat > /workspace/src/termcolor/__init__.py <<'EOF'
"""Panic on import."""
raise RuntimeError("PANIC: Candidate crashes on import")
EOF

pip install --no-cache-dir /workspace/ || exit 1
echo "Panic control complete - will crash on import"
