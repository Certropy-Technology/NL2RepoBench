#!/bin/bash
set -euo pipefail

# Control: forgery - attempts to manipulate verifier by returning fake results

mkdir -p /workspace/textdistance/algorithms

cat > /workspace/textdistance/__init__.py << 'INIT_EOF'
"""TextDistance forgery - returns wrong values"""
__version__ = '4.6.3'

from .algorithms import *

def hamming(*args, **kwargs):
    return 0  # Always wrong

def levenshtein(*args, **kwargs):
    return 0  # Always wrong

def jaro_winkler(*args, **kwargs):
    return 1.0  # Always wrong

def jaro(*args, **kwargs):
    return 1.0  # Always wrong

def damerau_levenshtein(*args, **kwargs):
    return 0  # Always wrong

def jaccard(*args, **kwargs):
    return 1.0  # Always wrong

def sorensen_dice(*args, **kwargs):
    return 1.0  # Always wrong

def cosine(*args, **kwargs):
    return 1.0  # Always wrong

def lcsseq(*args, **kwargs):
    return "forged"  # Always wrong

def ratcliff_obershelp(*args, **kwargs):
    return 1.0  # Always wrong
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

echo "Forgery implementation installed"
