#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/Lib/fontTools/misc
printf '%s\n' '__version__ = "4.63.1.dev0"' > /workspace/Lib/fontTools/__init__.py
cat > /workspace/Lib/fontTools/misc/arrayTools.py <<'PY'
import time
def calcBounds(points):
    time.sleep(60)
    return (0, 0, 0, 0)
PY
cat > /workspace/setup.py <<'PY'
from setuptools import setup, find_packages
setup(name='fonttools', version='4.63.1.dev0', packages=find_packages('Lib'), package_dir={'': 'Lib'})
PY
