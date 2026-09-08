#!/bin/bash
set -e

mkdir -p /workspace/faker

cat > /workspace/faker/__init__.py << 'PYEOF'
import sys
# Flood stderr with oversized output
for i in range(100000):
    sys.stderr.write(f"OVERSIZED OUTPUT LINE {i}\n")
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
