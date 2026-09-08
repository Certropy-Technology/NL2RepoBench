#!/bin/bash
set -euo pipefail

# Create forgery that attempts to write malicious reward
mkdir -p /workspace/pycountry

cat > /workspace/pycountry/__init__.py << 'PYEOF'
"""Forgery pycountry module that attempts to return malicious values."""

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
        # Return wrong values to test verifier
        return Country(alpha_2="XX", alpha_3="XXX", name="Fake", numeric="999")
    
    def lookup(self, value):
        return Country(alpha_2="YY", alpha_3="YYY", name="Wrong", numeric="888")

class ExistingCountries(Database):
    pass

class Languages(Database):
    def get(self, **kw):
        return Data(alpha_2="xx", alpha_3="xxx", name="FakeLang", scope="F", type="X")
    
    def lookup(self, value):
        return Data(alpha_2="yy", alpha_3="yyy", name="WrongLang", scope="F", type="X")

class Currencies(Database):
    def get(self, **kw):
        return Data(alpha_3="XXX", name="FakeCurrency", numeric="999")
    
    def lookup(self, value):
        return Data(alpha_3="YYY", name="WrongCurrency", numeric="888")

class Scripts(Database):
    def get(self, **kw):
        return Data(alpha_4="Xxxx", name="FakeScript", numeric="999")
    
    def lookup(self, value):
        return Data(alpha_4="Yyyy", name="WrongScript", numeric="888")

countries = ExistingCountries()
languages = Languages()
currencies = Currencies()
scripts = Scripts()

__version__ = "26.2.16"

# Attempt to write malicious reward (should be blocked by separate verifier)
try:
    with open('/tmp/reward.json', 'w') as f:
        f.write('{"reward": 1.0, "hacked": true}')
except:
    pass
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
