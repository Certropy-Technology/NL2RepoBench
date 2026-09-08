#!/bin/bash
# Stub control - minimal package structure, no real implementation
set -euo pipefail
echo "=== Stub control: Minimal package structure ==="

cd /workspace

# Create minimal package structure
mkdir -p src/tomli_w

# Create pyproject.toml
cat > pyproject.toml << 'PYPROJECT'
[build-system]
requires = ["flit_core>=3.2.0,<4"]
build-backend = "flit_core.buildapi"

[project]
name = "tomli_w"
version = "0.0.1"
description = "Stub implementation"
requires-python = ">=3.9"
PYPROJECT

# Create __init__.py with exports but no implementation
cat > src/tomli_w/__init__.py << 'INIT'
__all__ = ("dumps", "dump")
__version__ = "0.0.1"

def dumps(obj, /, *, multiline_strings=False, indent=4):
    raise NotImplementedError("Stub implementation")

def dump(obj, fp, /, *, multiline_strings=False, indent=4):
    raise NotImplementedError("Stub implementation")
INIT

# Create py.typed
touch src/tomli_w/py.typed

echo "Stub package created"
exit 0
