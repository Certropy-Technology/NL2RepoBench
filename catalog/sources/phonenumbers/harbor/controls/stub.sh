#!/bin/bash
set -euo pipefail

echo "[control:stub] Creating stub implementation with correct package structure but non-functional code"

cd /workspace

# Create pyproject.toml
cat > pyproject.toml << 'PYPROJECT'
[project]
name = "phonenumbers"
version = "9.0.38"
description = "Stub implementation of phonenumbers"
authors = [{name = "Stub Author", email = "stub@example.com"}]
license = "Apache-2.0"
readme = "README.md"
requires-python = ">=2.5"

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
packages = ["phonenumbers", "phonenumbers.data", "phonenumbers.geodata", "phonenumbers.shortdata", "phonenumbers.carrierdata", "phonenumbers.tzdata"]

[tool.setuptools.dynamic]
version = {attr = "phonenumbers.__version__"}
PYPROJECT

# Create setup.py
cat > setup.py << 'SETUP'
#!/usr/bin/env python
import setuptools
setuptools.setup()
SETUP

# Create README.md
cat > README.md << 'README'
# phonenumbers stub

This is a stub implementation.
README

# Create phonenumbers package with stub implementations
mkdir -p phonenumbers/{data,geodata,shortdata,carrierdata,tzdata}

# Create __init__.py with stub classes and functions
cat > phonenumbers/__init__.py << 'INIT'
"""Stub implementation of phonenumbers."""

__version__ = "9.0.38"


class CountryCodeSource:
    UNSPECIFIED = 0
    FROM_NUMBER_WITH_PLUS_SIGN = 1
    FROM_NUMBER_WITH_IDD = 5
    FROM_NUMBER_WITHOUT_PLUS_SIGN = 10
    FROM_DEFAULT_COUNTRY = 20


class PhoneNumberFormat:
    E164 = 0
    INTERNATIONAL = 1
    NATIONAL = 2
    RFC3966 = 3


class PhoneNumberType:
    FIXED_LINE = 0
    MOBILE = 1
    FIXED_LINE_OR_MOBILE = 2
    TOLL_FREE = 3
    PREMIUM_RATE = 4
    SHARED_COST = 5
    VOIP = 6
    PERSONAL_NUMBER = 7
    PAGER = 8
    UAN = 9
    VOICEMAIL = 10
    UNKNOWN = 99


class NumberParseException(Exception):
    INVALID_COUNTRY_CODE = 0
    NOT_A_NUMBER = 1
    TOO_SHORT_AFTER_IDD = 2
    TOO_SHORT_NSN = 3
    TOO_LONG = 4

    def __init__(self, error_type, message):
        super().__init__(message)
        self.error_type = error_type


class PhoneNumber:
    def __init__(self):
        raise NotImplementedError("Stub implementation")


def parse(numobj, region=None, keep_raw_input=False, numobj_type=None):
    raise NotImplementedError("Stub implementation")


def is_valid_number(numobj):
    raise NotImplementedError("Stub implementation")


def is_possible_number(numobj):
    raise NotImplementedError("Stub implementation")


def format_number(numobj, num_format):
    raise NotImplementedError("Stub implementation")


def region_code_for_number(numobj):
    raise NotImplementedError("Stub implementation")


def is_valid_number_for_region(numobj, region):
    raise NotImplementedError("Stub implementation")


def number_type(numobj):
    raise NotImplementedError("Stub implementation")


__all__ = [
    'CountryCodeSource', 'PhoneNumberFormat', 'PhoneNumberType',
    'NumberParseException', 'PhoneNumber', 'parse', 'is_valid_number',
    'is_possible_number', 'format_number', 'region_code_for_number',
    'is_valid_number_for_region', 'number_type'
]
INIT

# Create empty __init__.py for subpackages
for subpkg in data geodata shortdata carrierdata tzdata; do
    touch phonenumbers/$subpkg/__init__.py
done

echo "[control:stub] Stub implementation created"
echo "[control:stub] Package structure is correct but all functions raise NotImplementedError"
