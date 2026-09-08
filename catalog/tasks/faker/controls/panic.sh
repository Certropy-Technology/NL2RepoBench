#!/bin/bash
set -e

mkdir -p /workspace/faker

cat > /workspace/faker/__init__.py << 'PYEOF'
raise RuntimeError("PANIC: Import causes immediate failure")
PYEOF

cat > /workspace/setup.py << 'PYEOF'
from setuptools import setup

setup(
    name="Faker",
    version="40.38.0",
    packages=["faker"],
)
PYEOF

exit 0
