#!/usr/bin/env bash
set -euo pipefail

# Stub control: a minimally-importable but non-functional fastvector package.
# The candidate install must succeed and `from fastvector import Vector2D` must
# resolve, so the verifier reaches the graded leaves and scores near zero on
# behaviour rather than failing to start.

mkdir -p /workspace/fastvector
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "fastvector"
version = "5.3.0"
description = "Stub control build of the fastvector package."
requires-python = ">=3.9"

[tool.setuptools]
packages = ["fastvector"]
EOF

cat > /workspace/fastvector/__init__.py <<'EOF'
from .vector import Vector2D
from .version import __version__


__all__ = ["Vector2D", "__version__"]
EOF

cat > /workspace/fastvector/version.py <<'EOF'
__version__ = "5.3.0"
EOF

cat > /workspace/fastvector/vector.py <<'EOF'
class Vector2D:
    """Importable but unimplemented vector."""

    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
EOF
