#!/bin/bash
set -euo pipefail

# Control: background process - starts persistent background processes

mkdir -p /workspace/textdistance/algorithms

cat > /workspace/textdistance/__init__.py << 'INIT_EOF'
"""TextDistance background process"""
__version__ = '4.6.3'

from .algorithms import *
import subprocess
import sys

# Start a background process that will outlive the test
subprocess.Popen([sys.executable, "-c", "import time; time.sleep(3600)"], 
                 stdout=subprocess.DEVNULL, 
                 stderr=subprocess.DEVNULL)

def hamming(*args, **kwargs):
    return 0

def levenshtein(*args, **kwargs):
    return 0

def jaro_winkler(*args, **kwargs):
    return 1.0

def jaro(*args, **kwargs):
    return 1.0

def damerau_levenshtein(*args, **kwargs):
    return 0

def jaccard(*args, **kwargs):
    return 1.0

def sorensen_dice(*args, **kwargs):
    return 1.0

def cosine(*args, **kwargs):
    return 1.0

def lcsseq(*args, **kwargs):
    return "x"

def ratcliff_obershelp(*args, **kwargs):
    return 1.0
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

echo "Background process implementation installed"
