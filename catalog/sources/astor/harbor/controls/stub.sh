#!/bin/bash
set -euo pipefail

echo "[control:stub] Creating stub implementation with correct package structure but non-functional code"

cd /workspace

# Create setup.py
cat > setup.py << 'SETUP'
from setuptools import setup, find_packages

setup(
    name='astor',
    version='0.8.1',
    description='Stub implementation',
    author='Stub',
    author_email='stub@example.com',
    license='BSD-3-Clause',
    packages=find_packages(),
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
)
SETUP

# Create astor package
mkdir -p astor

# Create VERSION file
echo "0.8.1" > astor/VERSION

# Create __init__.py with stub functions that raise NotImplementedError
cat > astor/__init__.py << 'INIT'
"""Stub implementation of astor."""
import os

ROOT = os.path.dirname(__file__)
with open(os.path.join(ROOT, 'VERSION')) as version_file:
    __version__ = version_file.read().strip()

def to_source(node, indent_with=' ' * 4, add_line_information=False, pretty_source=None):
    raise NotImplementedError("Stub implementation")

def dump_tree(node, indent='  ', **kw):
    raise NotImplementedError("Stub implementation")

def parse_file(filename):
    raise NotImplementedError("Stub implementation")

class CodeToAst:
    def parse_file(self, filename):
        raise NotImplementedError("Stub implementation")

code_to_ast = CodeToAst()

class SourceGenerator:
    def __init__(self, indent_with, node=None):
        raise NotImplementedError("Stub implementation")
    
    def to_source(self):
        raise NotImplementedError("Stub implementation")

class ExplicitNodeVisitor:
    def __init__(self):
        raise NotImplementedError("Stub implementation")

class TreeWalk:
    def __init__(self):
        raise NotImplementedError("Stub implementation")

def iter_node(node):
    raise NotImplementedError("Stub implementation")

def strip_tree(node):
    raise NotImplementedError("Stub implementation")

def get_op_symbol(op, name):
    raise NotImplementedError("Stub implementation")

def get_op_precedence(node):
    raise NotImplementedError("Stub implementation")

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
"""Stub module."""
raise NotImplementedError("Stub implementation")
MODEOF
done

echo "[control:stub] Stub implementation created"
echo "[control:stub] Package structure is correct but all functions raise NotImplementedError"
