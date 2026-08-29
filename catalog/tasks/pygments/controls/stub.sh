#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/pygments
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools==80.10.2", "wheel==0.45.1"]
build-backend = "setuptools.build_meta"
[project]
name = "Pygments"
version = "2.21.0"
EOF
cat > /workspace/pygments/__init__.py <<'PY'
__version__ = "2.21.0"
def lex(*args, **kwargs): return []
def format(*args, **kwargs): return ""
def highlight(*args, **kwargs): return ""
PY
