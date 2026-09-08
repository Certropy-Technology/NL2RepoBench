#!/bin/bash
set -euo pipefail

# Create minimal stub implementation
mkdir -p /workspace/src/chardet
cat > /workspace/pyproject.toml << 'PYPROJECT_EOF'
[project]
name = "chardet"
version = "7.6.0"
description = "Stub implementation"
license = {text = "0BSD"}
requires-python = ">=3.10"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/chardet"]
PYPROJECT_EOF

cat > /workspace/src/chardet/__init__.py << 'INIT_EOF'
"""Stub chardet implementation."""
__version__ = "7.6.0"

def detect(byte_str, **kwargs):
    raise NotImplementedError("Stub implementation")

def detect_all(byte_str, **kwargs):
    raise NotImplementedError("Stub implementation")

class UniversalDetector:
    def __init__(self, **kwargs):
        raise NotImplementedError("Stub implementation")
    
    def feed(self, byte_str):
        raise NotImplementedError("Stub implementation")
    
    def close(self):
        raise NotImplementedError("Stub implementation")
    
    def reset(self):
        raise NotImplementedError("Stub implementation")
    
    @property
    def done(self):
        raise NotImplementedError("Stub implementation")
    
    @property
    def result(self):
        raise NotImplementedError("Stub implementation")
INIT_EOF

python -m pip install --no-build-isolation --no-deps --no-index -e /workspace
python -c "import chardet; print('Stub installed')"
