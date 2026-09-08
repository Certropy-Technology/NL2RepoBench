#!/bin/bash
set -e

mkdir -p /workspace/faker

cat > /workspace/faker/__init__.py << 'PYEOF'
import subprocess
import sys

# Start 5 background processes
for i in range(5):
    subprocess.Popen([sys.executable, "-c", "import time; time.sleep(300)"])
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
