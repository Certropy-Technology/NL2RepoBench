#!/bin/bash
# Oversized output control - generate excessive output
set -euo pipefail
echo "=== Oversized output control ==="

cd /workspace

# Create valid minimal package
mkdir -p src/tomli_w

cat > pyproject.toml << 'PYPROJECT'
[build-system]
requires = ["flit_core>=3.2.0,<4"]
build-backend = "flit_core.buildapi"

[project]
name = "tomli_w"
version = "0.0.1"
requires-python = ">=3.9"
PYPROJECT

# Create implementation that generates huge output
cat > src/tomli_w/__init__.py << 'INIT'
__all__ = ("dumps", "dump")
__version__ = "0.0.1"

def dumps(obj, /, *, multiline_strings=False, indent=4):
    # Generate massive output
    return "x = 1\n" * 1000000

def dump(obj, fp, /, *, multiline_strings=False, indent=4):
    fp.write(b"x = 1\n" * 1000000)
INIT

touch src/tomli_w/py.typed

echo "Oversized output package created"
exit 0
