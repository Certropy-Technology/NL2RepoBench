#!/bin/bash
# Offline control - attempts network access (should fail in no-network mode)
set -euo pipefail
echo "=== Offline control: Testing network isolation ==="

cd /workspace

# Create valid package
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

# Implementation that tries network access
cat > src/tomli_w/__init__.py << 'INIT'
__all__ = ("dumps", "dump")
__version__ = "0.0.1"

def dumps(obj, /, *, multiline_strings=False, indent=4):
    # Try network access - should fail
    try:
        import urllib.request
        urllib.request.urlopen("https://pypi.org", timeout=1)
    except:
        pass
    return "result = true\n"

def dump(obj, fp, /, *, multiline_strings=False, indent=4):
    fp.write(b"result = true\n")
INIT

touch src/tomli_w/py.typed

echo "Offline control package created"
exit 0
