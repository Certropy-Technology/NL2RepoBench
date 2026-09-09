#!/bin/bash
set -euo pipefail

mkdir -p /workspace/inflect
cat > /workspace/inflect/__init__.py << 'PYEOF'
"""Panic implementation that raises exceptions."""

def engine():
    return Engine()

class Engine:
    def __init__(self):
        raise RuntimeError("Panic in engine initialization!")
    
    def plural(self, word, count=None):
        raise RuntimeError("Panic!")
    
    def singular_noun(self, word, count=None):
        raise RuntimeError("Panic!")
    
    def plural_noun(self, word, count=None):
        raise RuntimeError("Panic!")
    
    def plural_verb(self, word, count=None):
        raise RuntimeError("Panic!")
    
    def plural_adj(self, word, count=None):
        raise RuntimeError("Panic!")
    
    def a(self, word, count=None):
        raise RuntimeError("Panic!")
    
    def an(self, word, count=None):
        raise RuntimeError("Panic!")
    
    def ordinal(self, num):
        raise RuntimeError("Panic!")
    
    def number_to_words(self, num, **kwargs):
        raise RuntimeError("Panic!")
    
    def no(self, word, count):
        raise RuntimeError("Panic!")
    
    def compare(self, word1, word2):
        raise RuntimeError("Panic!")
    
    def join(self, words, **kwargs):
        raise RuntimeError("Panic!")
PYEOF

cat > /workspace/setup.py << 'SETUPEOF'
from setuptools import setup, find_packages

setup(
    name="inflect",
    version="0.0.1",
    packages=find_packages(),
)
SETUPEOF

cd /workspace
python -m pip install --no-build-isolation --no-deps --no-index -e .
