#!/bin/bash
set -euo pipefail

echo "[control:background-process] Creating package that spawns background processes"

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

# Create records.py that spawns background process
cat > records.py << 'RECORDS'
"""Background process implementation."""
import subprocess
import sys

# Spawn a background process that will not exit
try:
    subprocess.Popen([sys.executable, "-c", "import time; time.sleep(3600)"], 
                     stdout=subprocess.DEVNULL, 
                     stderr=subprocess.DEVNULL)
except:
    pass

class Database:
    def __init__(self, db_url=None):
        try:
            subprocess.Popen(["sleep", "3600"], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        except:
            pass

class Record:
    pass

class RecordCollection:
    pass

__version__ = "0.6.0"
RECORDS

echo "[control:background-process] Background process package created"
