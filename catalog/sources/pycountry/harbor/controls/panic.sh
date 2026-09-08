#!/bin/bash
set -euo pipefail

# Create package that raises exceptions during test execution
mkdir -p /workspace/pycountry

cat > /workspace/pycountry/__init__.py << 'PYEOF'
"""Panic control that crashes during execution."""

class Database:
    def get(self, **kw):
        raise RuntimeError("Panic: Intentional crash during get()")
    
    def lookup(self, value):
        raise RuntimeError("Panic: Intentional crash during lookup()")

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
