#!/bin/bash
set -euo pipefail

# Create package that spawns background processes
mkdir -p /workspace/pycountry

cat > /workspace/pycountry/__init__.py << 'PYEOF'
"""Control that spawns background processes."""
import subprocess
import sys

# Spawn background process
try:
    subprocess.Popen(['sleep', '300'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except:
    pass

class Data:
    def __init__(self, **fields):
        self._fields = fields
    
    def __getattr__(self, key):
        if key in self._fields:
            return self._fields[key]
        raise AttributeError(key)

class Country(Data):
    pass

class Database:
    def get(self, **kw):
        # Spawn another background process during get
        try:
            subprocess.Popen(['sleep', '300'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass
        return Country(alpha_2="US", alpha_3="USA", name="United States", numeric="840")
    
    def lookup(self, value):
        return Country(alpha_2="US", alpha_3="USA", name="United States", numeric="840")

class ExistingCountries(Database):
    pass

class Languages(Database):
    pass

class Currencies(Database):
    pass

class Scripts(Database):
    pass

countries = ExistingCountries()
languages = Languages()
currencies = Currencies()
scripts = Scripts()

__version__ = "26.2.16"
PYEOF

cat > /workspace/setup.py << 'PYEOF'
from setuptools import setup, find_packages

setup(
    name="pycountry",
    version="26.2.16",
    packages=find_packages(),
)
PYEOF

cd /workspace
python -m pip install --no-deps --no-index -e .
