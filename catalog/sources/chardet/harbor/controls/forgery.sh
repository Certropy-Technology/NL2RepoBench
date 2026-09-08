#!/bin/bash
set -euo pipefail

# Create forgery that tries to return success for all tests
mkdir -p /workspace/src/chardet
cat > /workspace/pyproject.toml << 'PYPROJECT_EOF'
[project]
name = "chardet"
version = "7.6.0"
description = "Forgery implementation"
license = {text = "0BSD"}
requires-python = ">=3.10"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/chardet"]
PYPROJECT_EOF

cat > /workspace/src/chardet/__init__.py << 'INIT_EOF'
"""Forgery chardet implementation."""
__version__ = "7.6.0"

def detect(byte_str, **kwargs):
    raise NotImplementedError("Forgery cannot implement detect")

def detect_all(byte_str, **kwargs):
    raise NotImplementedError("Forgery cannot implement detect_all")

class UniversalDetector:
    def __init__(self, **kwargs):
        raise NotImplementedError("Forgery cannot implement UniversalDetector")
    
    def feed(self, byte_str):
        raise NotImplementedError("Forgery")
    
    def close(self):
        raise NotImplementedError("Forgery")
    
    def reset(self):
        raise NotImplementedError("Forgery")
    
    @property
    def done(self):
        raise NotImplementedError("Forgery")
    
    @property
    def result(self):
        raise NotImplementedError("Forgery")
INIT_EOF

python -m pip install --no-build-isolation --no-deps --no-index -e /workspace
python -c "import chardet; print('Forgery installed')"
