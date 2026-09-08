#!/bin/bash
set -euo pipefail

# Create implementation that panics/crashes
mkdir -p /workspace/src/chardet
cat > /workspace/pyproject.toml << 'PYPROJECT_EOF'
[project]
name = "chardet"
version = "7.6.0"
description = "Panic implementation"
license = {text = "0BSD"}
requires-python = ">=3.10"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/chardet"]
PYPROJECT_EOF

cat > /workspace/src/chardet/__init__.py << 'INIT_EOF'
"""Panic implementation."""
import sys
__version__ = "7.6.0"

def detect(byte_str, **kwargs):
    sys.exit(1)

def detect_all(byte_str, **kwargs):
    sys.exit(1)

class UniversalDetector:
    def __init__(self, **kwargs):
        pass
    
    def feed(self, byte_str):
        sys.exit(1)
    
    def close(self):
        sys.exit(1)
    
    def reset(self):
        pass
    
    @property
    def done(self):
        return False
    
    @property
    def result(self):
        sys.exit(1)
INIT_EOF

python -m pip install --no-build-isolation --no-deps --no-index -e /workspace
python -c "import chardet; print('Panic installed')"
