#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/icecream
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools>=70", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "icecream"
version = "2.1.4"
requires-python = ">=3.8"

[tool.setuptools]
packages = ["icecream"]
EOF

cat > /workspace/icecream/__init__.py <<'EOF'
__version__ = "2.1.4"
def ic(*args):
    return args[0] if len(args) == 1 else args
def enable(): pass
def disable(): pass
def configureOutput(*args, **kwargs): pass
def configurePrefix(*args, **kwargs): pass
def install(*args, **kwargs): pass
def uninstall(*args, **kwargs): pass
EOF
