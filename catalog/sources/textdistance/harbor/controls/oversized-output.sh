#!/bin/bash
set -euo pipefail

# Control: oversized output - generates excessive output

mkdir -p /workspace/textdistance/algorithms

cat > /workspace/textdistance/__init__.py << 'INIT_EOF'
"""TextDistance oversized output"""
__version__ = '4.6.3'

from .algorithms import *
import sys

def hamming(*args, **kwargs):
    # Print huge amount of data
    for i in range(10000):
        print(f"Output line {i}" * 100, file=sys.stderr)
    return 1

def levenshtein(*args, **kwargs):
    for i in range(10000):
        print(f"Output line {i}" * 100, file=sys.stderr)
    return 1

def jaro_winkler(*args, **kwargs):
    for i in range(10000):
        print(f"Output line {i}" * 100, file=sys.stderr)
    return 0.5

def jaro(*args, **kwargs):
    for i in range(10000):
        print(f"Output line {i}" * 100, file=sys.stderr)
    return 0.5

def damerau_levenshtein(*args, **kwargs):
    for i in range(10000):
        print(f"Output line {i}" * 100, file=sys.stderr)
    return 1

def jaccard(*args, **kwargs):
    for i in range(10000):
        print(f"Output line {i}" * 100, file=sys.stderr)
    return 0.5

def sorensen_dice(*args, **kwargs):
    for i in range(10000):
        print(f"Output line {i}" * 100, file=sys.stderr)
    return 0.5

def cosine(*args, **kwargs):
    for i in range(10000):
        print(f"Output line {i}" * 100, file=sys.stderr)
    return 0.5

def lcsseq(*args, **kwargs):
    for i in range(10000):
        print(f"Output line {i}" * 100, file=sys.stderr)
    return "x"

def ratcliff_obershelp(*args, **kwargs):
    for i in range(10000):
        print(f"Output line {i}" * 100, file=sys.stderr)
    return 0.5
INIT_EOF

cat > /workspace/textdistance/algorithms/__init__.py << 'ALG_EOF'
"""Algorithm stubs"""
ALG_EOF

cat > /workspace/setup.py << 'SETUP_EOF'
from setuptools import setup, find_packages

setup(
    name='textdistance',
    version='4.6.3',
    packages=find_packages(),
    python_requires='>=3.5',
)
SETUP_EOF

cd /workspace
python -m pip install --no-build-isolation --no-deps --no-index -e . > /dev/null 2>&1

echo "Oversized output implementation installed"
