#!/bin/bash
set -euo pipefail

# Create implementation that spawns background processes
mkdir -p /workspace/humanfriendly

cat > /workspace/humanfriendly/__init__.py << 'BACKGROUND_INIT'
import subprocess
import time

__version__ = '10.0'

class InvalidSize(Exception):
    pass

class InvalidTimespan(Exception):
    pass

class InvalidLength(Exception):
    pass

# Spawn background process
subprocess.Popen(['sleep', '300'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def format_size(num_bytes, keep_width=False, binary=False):
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
BACKGROUND_INIT

cat > /workspace/humanfriendly/text.py << 'BACKGROUND_TEXT'
def pluralize(count, singular, plural=None):
    raise NotImplementedError()

def concatenate(items):
    raise NotImplementedError()
BACKGROUND_TEXT

cat > /workspace/humanfriendly/tables.py << 'BACKGROUND_TABLES'
def format_pretty_table(data):
    raise NotImplementedError()

def format_table(data):
    raise NotImplementedError()
BACKGROUND_TABLES

cat > /workspace/setup.py << 'BACKGROUND_SETUP'
from setuptools import setup, find_packages

setup(
    name='humanfriendly',
    version='10.0',
    packages=find_packages(),
)
BACKGROUND_SETUP

cd /workspace
python -m pip install --no-build-isolation --no-deps --no-index -e .

echo "Background process implementation installed"
