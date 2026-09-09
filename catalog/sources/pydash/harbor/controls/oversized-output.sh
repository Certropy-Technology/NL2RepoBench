#!/bin/bash
# oversized-output.sh - Install module that produces excessive output
set -euo pipefail

cat > /workspace/pydash.py << 'PYOVERSIZED'
"""Module that floods stdout."""
import sys

# Print 100KB of data on every function call
LARGE_OUTPUT = "X" * 102400

def chunk(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return []

def compact(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return []

def first(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return None

def last(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return None

def flatten(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return []

def flatten_deep(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return []

def initial(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return []

def take(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return []

def take_right(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return []

def union(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return []

def uniq(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return []

def without(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return []

def get(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return None

def has(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return False

def set_(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    pass

def unset(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    pass

def map_(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return []

def filter_(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return []

def reduce_(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return None

def group_by(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return {}

def key_by(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return {}

def find(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return None

def find_index(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return -1

def every(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return False

def some(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return False

def includes(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return False

def is_empty(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return False

def is_equal(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return False

def merge(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return {}

def pick(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return {}

def omit(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return {}

def keys(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return []

def values(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return []

def invert(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return {}

def defaults(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return {}

def negate(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return lambda x: False

def times(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return []

def identity(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return None

def constant(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return lambda: None

def range_(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return []

def camel_case(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return ""

def snake_case(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return ""

def kebab_case(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return ""

def capitalize(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return ""

def upper_first(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return ""

def lower_first(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return ""

def truncate(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return ""

def intersection(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return []

def difference(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return []

def zip_(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return []

def unzip(*args, **kwargs):
    print(LARGE_OUTPUT, file=sys.stderr)
    return []

__version__ = "0.0.0-oversized"
PYOVERSIZED

echo "Oversized output pydash module installed"
