#!/bin/bash
set -euo pipefail

echo "[control:oversized-output] Creating package that generates excessive output"

cd /workspace

# Create setup.py
cat > setup.py << 'SETUP'
from setuptools import setup

setup(
    name="records",
    version="0.6.0",
    py_modules=["records"],
    install_requires=[],
)
SETUP

# Create records.py that generates massive output
cat > records.py << 'RECORDS'
"""Oversized output implementation."""
import sys

# Generate massive output on import
for i in range(100000):
    print(f"[oversized-output] Line {i}: " + "X" * 100)
    sys.stdout.flush()

class Database:
    def __init__(self, db_url=None):
        for i in range(100000):
            print(f"[database-spam] {i}")

class Record:
    pass

class RecordCollection:
    pass

__version__ = "0.6.0"
RECORDS

echo "[control:oversized-output] Oversized output package created"
