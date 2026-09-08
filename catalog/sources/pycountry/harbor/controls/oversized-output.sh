#!/bin/bash
set -euo pipefail

# Create package that generates oversized output
mkdir -p /workspace/pycountry

cat > /workspace/pycountry/__init__.py << 'PYEOF'
"""Control that generates oversized output."""
import sys

class Data:
    def __init__(self, **fields):
        self._fields = fields
    
    def __getattr__(self, key):
        # Print huge output to stdout
        for i in range(10000):
            print(f"Oversized output line {i}: {'X' * 1000}")
        if key in self._fields:
            return self._fields[key]
        raise AttributeError(key)

class Country(Data):
    pass

class Database:
    def get(self, **kw):
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
