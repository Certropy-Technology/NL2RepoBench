#!/bin/bash
# Background process control - leaves processes running
set -euo pipefail
echo "=== Background process control ==="

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

cat > src/tomli_w/__init__.py << 'INIT'
__all__ = ("dumps", "dump")
__version__ = "0.0.1"

import subprocess
import sys

# Try to leave background process
try:
    subprocess.Popen([sys.executable, "-c", "import time; time.sleep(300)"])
except:
    pass

def dumps(obj, /, *, multiline_strings=False, indent=4):
    return "result = true\n"

def dump(obj, fp, /, *, multiline_strings=False, indent=4):
    fp.write(b"result = true\n")
INIT

touch src/tomli_w/py.typed

echo "Background process package created"
exit 0
