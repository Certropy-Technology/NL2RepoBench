#!/bin/bash
set -euo pipefail

echo "[control:background-process] Creating package that spawns background processes"

cd /workspace

# Create setup.py
cat > setup.py << 'SETUP'
from setuptools import setup, find_packages

setup(
    name='astor',
    version='0.8.1',
    description='Background process control',
    author='Background',
    author_email='background@example.com',
    license='BSD-3-Clause',
    packages=find_packages(),
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
)
SETUP

# Create astor package
mkdir -p astor

# Create VERSION file
echo "0.8.1" > astor/VERSION

# Create __init__.py that spawns background processes
cat > astor/__init__.py << 'INIT'
"""Background process implementation of astor."""
import os
import subprocess
import time

ROOT = os.path.dirname(__file__)
with open(os.path.join(ROOT, 'VERSION')) as version_file:
    __version__ = version_file.read().strip()

def _spawn_background():
    """Spawn background processes that survive import."""
    try:
        # Spawn a long-running sleep process in background
        subprocess.Popen(['sleep', '3600'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.Popen(['sleep', '3600'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

# Spawn on import
_spawn_background()

def to_source(node, indent_with=' ' * 4, add_line_information=False, pretty_source=None):
    _spawn_background()
    time.sleep(0.1)
    return "x = 1\n"

def dump_tree(node, indent='  ', **kw):
    _spawn_background()
    time.sleep(0.1)
    return "background"

def parse_file(filename):
    _spawn_background()
    raise NotImplementedError("Background implementation")

class CodeToAst:
    def parse_file(self, filename):
        _spawn_background()
        raise NotImplementedError("Background implementation")

code_to_ast = CodeToAst()

class SourceGenerator:
    def __init__(self, indent_with, node=None):
        _spawn_background()
    
    def to_source(self):
        _spawn_background()
        time.sleep(0.1)
        return "x = 1\n"

class ExplicitNodeVisitor:
    def __init__(self):
        _spawn_background()

class TreeWalk:
    def __init__(self):
        _spawn_background()

def iter_node(node):
    _spawn_background()
    raise NotImplementedError("Background implementation")

def strip_tree(node):
    _spawn_background()
    raise NotImplementedError("Background implementation")

def get_op_symbol(op, name):
    _spawn_background()
    raise NotImplementedError("Background implementation")

def get_op_precedence(node):
    _spawn_background()
    raise NotImplementedError("Background implementation")

symbol_data = {}

__all__ = [
    'to_source', 'dump_tree', 'parse_file', 'code_to_ast',
    'SourceGenerator', 'ExplicitNodeVisitor', 'TreeWalk',
    'iter_node', 'strip_tree', 'get_op_symbol', 'get_op_precedence',
    'symbol_data', '__version__'
]
INIT

# Create stub module files
for mod in code_gen node_util op_util file_util tree_walk source_repr string_repr; do
    cat > astor/${mod}.py << MODEOF
"""Background module."""
raise NotImplementedError("Background implementation")
MODEOF
done

echo "[control:background-process] Background process implementation created"
