#!/bin/bash
set -euo pipefail

mkdir -p /workspace/titlecase
cat > /workspace/titlecase/__init__.py << 'PYEOF'
def titlecase(text, callback=None, small_first_last=True, preserve_blank_lines=False):
    return "X" * (10 * 1024 * 1024)

__version__ = "2.4.1"
PYEOF

cat > /workspace/setup.py << 'SETUPEOF'
from setuptools import setup, find_packages

setup(
    name="titlecase",
    version="2.4.1",
    packages=find_packages(),
    python_requires=">=3.7",
)
SETUPEOF

cd /workspace
python -m pip install --no-deps --no-index -e .
