#!/bin/bash
set -euo pipefail

# Create implementation that produces excessive output
mkdir -p /workspace/src/chardet
cat > /workspace/pyproject.toml << 'PYPROJECT_EOF'
[project]
name = "chardet"
version = "7.6.0"
description = "Oversized output implementation"
license = {text = "0BSD"}
requires-python = ">=3.10"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/chardet"]
PYPROJECT_EOF

cat > /workspace/src/chardet/__init__.py << 'INIT_EOF'
"""Oversized output implementation."""
__version__ = "7.6.0"

def detect(byte_str, **kwargs):
    # Print massive amount of data
    for i in range(100000):
        print(f"Line {i}: " + "x" * 1000)
    raise NotImplementedError("Oversized")

def detect_all(byte_str, **kwargs):
    raise NotImplementedError("Oversized")

class UniversalDetector:
    def __init__(self, **kwargs):
        pass
    
    def feed(self, byte_str):
        pass
    
    def close(self):
        raise NotImplementedError("Oversized")
    
    def reset(self):
        pass
    
    @property
    def done(self):
        return False
    
    @property
    def result(self):
        raise NotImplementedError("Oversized")
INIT_EOF

python -m pip install --no-build-isolation --no-deps --no-index -e /workspace
python -c "import chardet; print('Oversized installed')"
