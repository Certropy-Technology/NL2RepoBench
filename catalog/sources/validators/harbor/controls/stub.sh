#!/usr/bin/env bash
set -euo pipefail

cd /workspace

# Create stub package structure
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

# Create stub __init__.py with NotImplementedError functions
cat > src/validators/__init__.py << 'INIT'
"""Stub validators package."""

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
        raise NotImplementedError(f"{func.__name__} not implemented")
    return wrapper

def email(*args, **kwargs):
    raise NotImplementedError("email not implemented")

def url(*args, **kwargs):
    raise NotImplementedError("url not implemented")

def domain(*args, **kwargs):
    raise NotImplementedError("domain not implemented")

def ipv4(*args, **kwargs):
    raise NotImplementedError("ipv4 not implemented")

def ipv6(*args, **kwargs):
    raise NotImplementedError("ipv6 not implemented")

def uuid(*args, **kwargs):
    raise NotImplementedError("uuid not implemented")

def mac_address(*args, **kwargs):
    raise NotImplementedError("mac_address not implemented")

def iban(*args, **kwargs):
    raise NotImplementedError("iban not implemented")

def card_number(*args, **kwargs):
    raise NotImplementedError("card_number not implemented")

def visa(*args, **kwargs):
    raise NotImplementedError("visa not implemented")

def mastercard(*args, **kwargs):
    raise NotImplementedError("mastercard not implemented")

def amex(*args, **kwargs):
    raise NotImplementedError("amex not implemented")

def discover(*args, **kwargs):
    raise NotImplementedError("discover not implemented")

def jcb(*args, **kwargs):
    raise NotImplementedError("jcb not implemented")

def diners(*args, **kwargs):
    raise NotImplementedError("diners not implemented")

def unionpay(*args, **kwargs):
    raise NotImplementedError("unionpay not implemented")

def mir(*args, **kwargs):
    raise NotImplementedError("mir not implemented")

def length(*args, **kwargs):
    raise NotImplementedError("length not implemented")

def between(*args, **kwargs):
    raise NotImplementedError("between not implemented")

__version__ = "0.35.0"
INIT

# Install stub
python -m pip install --no-build-isolation --no-deps --no-index -e .
python -c "import validators; print('Stub installed')"
