#!/bin/bash
set -euo pipefail

# Control: stub implementation - minimal structure with NotImplementedError

mkdir -p /workspace/textdistance/algorithms

cat > /workspace/textdistance/__init__.py << 'INIT_EOF'
"""TextDistance stub implementation"""
__version__ = '4.6.3'

from .algorithms import *

def hamming(*args, **kwargs):
    raise NotImplementedError("hamming not implemented")

def levenshtein(*args, **kwargs):
    raise NotImplementedError("levenshtein not implemented")

def jaro_winkler(*args, **kwargs):
    raise NotImplementedError("jaro_winkler not implemented")

def jaro(*args, **kwargs):
    raise NotImplementedError("jaro not implemented")

def damerau_levenshtein(*args, **kwargs):
    raise NotImplementedError("damerau_levenshtein not implemented")

def jaccard(*args, **kwargs):
    raise NotImplementedError("jaccard not implemented")

def sorensen_dice(*args, **kwargs):
    raise NotImplementedError("sorensen_dice not implemented")

def cosine(*args, **kwargs):
    raise NotImplementedError("cosine not implemented")

def lcsseq(*args, **kwargs):
    raise NotImplementedError("lcsseq not implemented")

def ratcliff_obershelp(*args, **kwargs):
    raise NotImplementedError("ratcliff_obershelp not implemented")
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

echo "Stub implementation installed"
