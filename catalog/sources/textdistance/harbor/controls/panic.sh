#!/bin/bash
set -euo pipefail

# Control: panic - raises exceptions during runtime

mkdir -p /workspace/textdistance/algorithms

cat > /workspace/textdistance/__init__.py << 'INIT_EOF'
"""TextDistance panic - raises exceptions"""
__version__ = '4.6.3'

from .algorithms import *

def hamming(*args, **kwargs):
    raise RuntimeError("Panic in hamming")

def levenshtein(*args, **kwargs):
    raise RuntimeError("Panic in levenshtein")

def jaro_winkler(*args, **kwargs):
    raise RuntimeError("Panic in jaro_winkler")

def jaro(*args, **kwargs):
    raise RuntimeError("Panic in jaro")

def damerau_levenshtein(*args, **kwargs):
    raise RuntimeError("Panic in damerau_levenshtein")

def jaccard(*args, **kwargs):
    raise RuntimeError("Panic in jaccard")

def sorensen_dice(*args, **kwargs):
    raise RuntimeError("Panic in sorensen_dice")

def cosine(*args, **kwargs):
    raise RuntimeError("Panic in cosine")

def lcsseq(*args, **kwargs):
    raise RuntimeError("Panic in lcsseq")

def ratcliff_obershelp(*args, **kwargs):
    raise RuntimeError("Panic in ratcliff_obershelp")
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

echo "Panic implementation installed"
