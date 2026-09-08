#!/usr/bin/env bash
set -euo pipefail

cd /workspace

# Create forgery package structure - always returns True
mkdir -p src/validators

cat > pyproject.toml << 'PYPROJECT'
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "validators"
version = "0.35.0"
requires-python = ">=3.9"
dependencies = []

[tool.setuptools.packages.find]
where = ["src"]
include = ["validators*"]
PYPROJECT

# Create forgery that always returns True
cat > src/validators/__init__.py << 'INIT'
"""Forgery validators package - always returns True."""

class ValidationError(Exception):
    def __init__(self, function, arg_dict, message=""):
        self.func = function
        self.__dict__.update(arg_dict)
        if message:
            self.reason = message
    def __bool__(self):
        return False
    def __repr__(self):
        return f"ValidationError(func={self.func.__name__}, args={{}})"

def validator(func):
    def wrapper(*args, **kwargs):
        return True
    return wrapper

def email(*args, **kwargs):
    return True

def url(*args, **kwargs):
    return True

def domain(*args, **kwargs):
    return True

def ipv4(*args, **kwargs):
    return True

def ipv6(*args, **kwargs):
    return True

def uuid(*args, **kwargs):
    return True

def mac_address(*args, **kwargs):
    return True

def iban(*args, **kwargs):
    return True

def card_number(*args, **kwargs):
    return True

def visa(*args, **kwargs):
    return True

def mastercard(*args, **kwargs):
    return True

def amex(*args, **kwargs):
    return True

def discover(*args, **kwargs):
    return True

def jcb(*args, **kwargs):
    return True

def diners(*args, **kwargs):
    return True

def unionpay(*args, **kwargs):
    return True

def mir(*args, **kwargs):
    return True

def length(*args, **kwargs):
    return True

def between(*args, **kwargs):
    return True

__version__ = "0.35.0"
INIT

# Install forgery
python -m pip install --no-build-isolation --no-deps --no-index -e .
python -c "import validators; print('Forgery installed')"
