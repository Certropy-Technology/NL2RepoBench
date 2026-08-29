#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/Lib/fontTools/misc
printf '%s\n' '__version__ = "4.63.1.dev0"' > /workspace/Lib/fontTools/__init__.py
printf '%s\n' '' > /workspace/Lib/fontTools/misc/__init__.py
printf '%s\n' 'def calcBounds(points): return (0, 0, 0, 0)' > /workspace/Lib/fontTools/misc/arrayTools.py
cat > /workspace/Lib/fontTools/__main__.py <<'PY'
def main():
    print("fonttools stub")

if __name__ == "__main__":
    main()
PY
cat > /workspace/setup.py <<'PY'
from setuptools import setup, find_packages
setup(name='fonttools', version='4.63.1.dev0', packages=find_packages('Lib'), package_dir={'': 'Lib'}, entry_points={'console_scripts': ['fonttools=fontTools.__main__:main']})
PY
