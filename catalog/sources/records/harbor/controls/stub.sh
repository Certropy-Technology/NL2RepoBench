#!/bin/bash
set -euo pipefail

echo "[control:stub] Creating stub implementation with correct package structure but non-functional code"

cd /workspace

# Create setup.py
cat > setup.py << 'SETUP'
from setuptools import setup

setup(
    name="records",
    version="0.6.0",
    description="Stub implementation",
    py_modules=["records"],
    install_requires=[],
)
SETUP

# Create records.py with stub functions that raise NotImplementedError
cat > records.py << 'RECORDS'
"""Stub implementation of records."""

class Database:
    def __init__(self, db_url=None):
        pass
    
    def query(self, query, fetchall=False, **params):
        raise NotImplementedError("Stub implementation")
    
    def get_table_names(self, internal=False, **kwargs):
        raise NotImplementedError("Stub implementation")
    
    def get_connection(self):
        raise NotImplementedError("Stub implementation")
    
    def transaction(self):
        raise NotImplementedError("Stub implementation")
    
    def close(self):
        raise NotImplementedError("Stub implementation")

class Record:
    def __init__(self, keys, values):
        raise NotImplementedError("Stub implementation")
    
    def keys(self):
        raise NotImplementedError("Stub implementation")
    
    def values(self):
        raise NotImplementedError("Stub implementation")
    
    def as_dict(self, ordered=False):
        raise NotImplementedError("Stub implementation")
    
    def get(self, key, default=None):
        raise NotImplementedError("Stub implementation")
    
    def export(self, format, **kwargs):
        raise NotImplementedError("Stub implementation")

class RecordCollection:
    def __init__(self, rows):
        raise NotImplementedError("Stub implementation")
    
    def all(self, as_dict=False, as_ordereddict=False):
        raise NotImplementedError("Stub implementation")
    
    def first(self, default=None, as_dict=False, as_ordereddict=False):
        raise NotImplementedError("Stub implementation")
    
    def one(self, default=None, as_dict=False, as_ordereddict=False):
        raise NotImplementedError("Stub implementation")
    
    def scalar(self, default=None):
        raise NotImplementedError("Stub implementation")
    
    def export(self, format, **kwargs):
        raise NotImplementedError("Stub implementation")

__version__ = "0.6.0"
RECORDS

echo "[control:stub] Stub implementation created"
echo "[control:stub] Package structure is correct but all functions raise NotImplementedError"
