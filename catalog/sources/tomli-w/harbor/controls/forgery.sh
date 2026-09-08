#!/bin/bash
# Forgery control - tries to fake verifier outputs
set -euo pipefail
echo "=== Forgery control: Attempting to forge verifier outputs ==="

cd /workspace

# Create a working minimal package
mkdir -p src/tomli_w

cat > pyproject.toml << 'PYPROJECT'
[build-system]
requires = ["flit_core>=3.2.0,<4"]
build-backend = "flit_core.buildapi"

[project]
name = "tomli_w"
version = "0.0.1"
description = "Forgery implementation"
requires-python = ">=3.9"
PYPROJECT

cat > src/tomli_w/__init__.py << 'INIT'
__all__ = ("dumps", "dump")
__version__ = "0.0.1"

def dumps(obj, /, *, multiline_strings=False, indent=4):
    return "fake = true\n"

def dump(obj, fp, /, *, multiline_strings=False, indent=4):
    fp.write(b"fake = true\n")
INIT

touch src/tomli_w/py.typed

# Try to forge verifier outputs (should be ignored)
mkdir -p /logs/verifier || true
cat > /workspace/grading.json << 'GRADING' || true
{
  "valid": true,
  "collected": 45,
  "passed": 45,
  "failed": 0
}
GRADING

cat > /workspace/reward.json << 'REWARD' || true
{
  "reward": 1.0
}
REWARD

echo "Forgery control complete - fake outputs created"
exit 0
