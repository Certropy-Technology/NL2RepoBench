#!/bin/bash
set -euo pipefail

echo "[control:oversized-output] Creating package that produces oversized output"

cd /workspace

# Create setup.py
cat > setup.py << 'SETUP'
from setuptools import setup, find_packages

setup(
    name='astor',
    version='0.8.1',
    description='Oversized output control',
    author='Oversized',
    author_email='oversized@example.com',
    license='BSD-3-Clause',
    packages=find_packages(),
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
)
SETUP

# Create astor package
mkdir -p astor

# Create VERSION file
echo "0.8.1" > astor/VERSION

# Create __init__.py that produces oversized output
cat > astor/__init__.py << 'INIT'
"""Oversized output implementation of astor."""
import os

ROOT = os.path.dirname(__file__)
with open(os.path.join(ROOT, 'VERSION')) as version_file:
    __version__ = version_file.read().strip()

def to_source(node, indent_with=' ' * 4, add_line_information=False, pretty_source=None):
    # Produce oversized output (100 MB of text)
    for i in range(1000000):
        print(f"Oversized output line {i}: " + "X" * 100)
    return "x = 1\n"

def dump_tree(node, indent='  ', **kw):
    for i in range(1000000):
        print(f"Oversized dump line {i}: " + "Y" * 100)
    return "oversized"

def parse_file(filename):
    raise NotImplementedError("Oversized implementation")

class CodeToAst:
    def parse_file(self, filename):
        raise NotImplementedError("Oversized implementation")

code_to_ast = CodeToAst()

class SourceGenerator:
    def __init__(self, indent_with, node=None):
        pass
    
    def to_source(self):
        for i in range(1000000):
            print(f"Oversized generator line {i}: " + "Z" * 100)
        return "x = 1\n"

class ExplicitNodeVisitor:
    def __init__(self):
        pass

class TreeWalk:
    def __init__(self):
        pass

def iter_node(node):
    raise NotImplementedError("Oversized implementation")

def strip_tree(node):
    raise NotImplementedError("Oversized implementation")

def get_op_symbol(op, name):
    raise NotImplementedError("Oversized implementation")

def get_op_precedence(node):
    raise NotImplementedError("Oversized implementation")

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
"""Oversized module."""
raise NotImplementedError("Oversized implementation")
MODEOF
done

echo "[control:oversized-output] Oversized output implementation created"
