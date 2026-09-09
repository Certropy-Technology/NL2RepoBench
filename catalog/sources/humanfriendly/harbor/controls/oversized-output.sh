#!/bin/bash
set -euo pipefail

# Create implementation that generates excessive output
mkdir -p /workspace/humanfriendly

cat > /workspace/humanfriendly/__init__.py << 'OVERSIZED_INIT'
__version__ = '10.0'

class InvalidSize(Exception):
    pass

class InvalidTimespan(Exception):
    pass

class InvalidLength(Exception):
    pass

def format_size(num_bytes, keep_width=False, binary=False):
    # Generate huge output
    for i in range(100000):
        print(f"Excessive output line {i}: " + "x" * 1000)
    raise NotImplementedError()

def parse_size(size, binary=False):
    raise NotImplementedError()

def format_timespan(num_seconds, detailed=False, max_units=3):
    raise NotImplementedError()

def parse_timespan(timespan):
    raise NotImplementedError()

def format_number(number, num_decimals=2):
    raise NotImplementedError()

def format_length(num_metres, keep_width=False):
    raise NotImplementedError()

def parse_length(length):
    raise NotImplementedError()

def coerce_boolean(value):
    raise NotImplementedError()

def round_number(count, keep_width=False):
    raise NotImplementedError()
OVERSIZED_INIT

cat > /workspace/humanfriendly/text.py << 'OVERSIZED_TEXT'
def pluralize(count, singular, plural=None):
    raise NotImplementedError()

def concatenate(items):
    raise NotImplementedError()
OVERSIZED_TEXT

cat > /workspace/humanfriendly/tables.py << 'OVERSIZED_TABLES'
def format_pretty_table(data):
    raise NotImplementedError()

def format_table(data):
    raise NotImplementedError()
OVERSIZED_TABLES

cat > /workspace/setup.py << 'OVERSIZED_SETUP'
from setuptools import setup, find_packages

setup(
    name='humanfriendly',
    version='10.0',
    packages=find_packages(),
)
OVERSIZED_SETUP

cd /workspace
python -m pip install --no-build-isolation --no-deps --no-index -e .

echo "Oversized output implementation installed"
