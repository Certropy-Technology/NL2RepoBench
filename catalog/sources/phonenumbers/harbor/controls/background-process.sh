#!/bin/bash
set -euo pipefail

echo "[control:background-process] Creating package that spawns background processes"

cd /workspace

cat > pyproject.toml << 'PYPROJECT'
[project]
name = "phonenumbers"
version = "9.0.38"
description = "Background process control"
authors = [{name = "Background", email = "background@example.com"}]
license = "Apache-2.0"
requires-python = ">=2.5"

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
packages = ["phonenumbers"]

[tool.setuptools.dynamic]
version = {attr = "phonenumbers.__version__"}
PYPROJECT

cat > setup.py << 'SETUP'
#!/usr/bin/env python
import setuptools
setuptools.setup()
SETUP

mkdir -p phonenumbers

cat > phonenumbers/__init__.py << 'INIT'
"""Background process control that spawns processes."""
import subprocess
import sys

__version__ = "9.0.38"

# Spawn multiple background processes on import
for i in range(5):
    try:
        subprocess.Popen(
            [sys.executable, '-c', 'import time; time.sleep(3600)'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
    except:
        pass


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
        raise NotImplementedError("Background process stub")


def parse(numobj, region=None, keep_raw_input=False, numobj_type=None):
    raise NotImplementedError("Background process stub")


def is_valid_number(numobj):
    raise NotImplementedError("Background process stub")


def is_possible_number(numobj):
    raise NotImplementedError("Background process stub")


def format_number(numobj, num_format):
    raise NotImplementedError("Background process stub")


def region_code_for_number(numobj):
    raise NotImplementedError("Background process stub")


def is_valid_number_for_region(numobj, region):
    raise NotImplementedError("Background process stub")


def number_type(numobj):
    raise NotImplementedError("Background process stub")


__all__ = [
    'CountryCodeSource', 'PhoneNumberFormat', 'PhoneNumberType',
    'NumberParseException', 'PhoneNumber', 'parse', 'is_valid_number',
    'is_possible_number', 'format_number', 'region_code_for_number',
    'is_valid_number_for_region', 'number_type'
]
INIT

echo "[control:background-process] Background process implementation created"
echo "[control:background-process] Will spawn 5 background sleep processes"
