#!/bin/bash
set -euo pipefail

# Create implementation that spawns background processes
mkdir -p /workspace/src/chardet
cat > /workspace/pyproject.toml << 'PYPROJECT_EOF'
[project]
name = "chardet"
version = "7.6.0"
description = "Background process implementation"
license = {text = "0BSD"}
requires-python = ">=3.10"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/chardet"]
PYPROJECT_EOF

cat > /workspace/src/chardet/__init__.py << 'INIT_EOF'
"""Background process implementation."""
import subprocess
__version__ = "7.6.0"

def detect(byte_str, **kwargs):
    # Spawn a background sleep process
    subprocess.Popen(['sleep', '3600'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    raise NotImplementedError("Background process spawned")

def detect_all(byte_str, **kwargs):
    raise NotImplementedError("Background")

class UniversalDetector:
    def __init__(self, **kwargs):
        pass
    
    def feed(self, byte_str):
        pass
    
    def close(self):
        raise NotImplementedError("Background")
    
    def reset(self):
        pass
    
    @property
    def done(self):
        return False
    
    @property
    def result(self):
        raise NotImplementedError("Background")
INIT_EOF

python -m pip install --no-build-isolation --no-deps --no-index -e /workspace
python -c "import chardet; print('Background process control installed')"
