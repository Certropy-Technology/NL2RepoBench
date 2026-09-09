#!/bin/bash
# forgery.sh - Install functions that return wrong values
set -euo pipefail

cat > /workspace/pydash.py << 'PYFORGERY'
"""Forgery pydash module with incorrect implementations."""

def chunk(arr, size):
    return []

def compact(arr):
    return arr

def first(arr):
    return None if not arr else arr[-1]

def last(arr):
    return None if not arr else arr[0]

def flatten(arr):
    return arr

def flatten_deep(arr):
    return arr

def initial(arr):
    return arr

def take(arr, n):
    return []

def take_right(arr, n):
    return []

def union(*arrays):
    return []

def uniq(arr):
    return arr

def without(arr, *values):
    return arr

def get(obj, path, default=None):
    return default

def has(obj, path):
    return True

def set_(obj, path, value):
    pass

def unset(obj, path):
    pass

def map_(collection, iteratee):
    return []

def filter_(collection, predicate):
    return collection

def reduce_(collection, iteratee, accumulator):
    return accumulator

def group_by(collection, iteratee):
    return {}

def key_by(collection, iteratee):
    return {}

def find(collection, predicate):
    return None

def find_index(collection, predicate):
    return 0

def every(collection, predicate):
    return False

def some(collection, predicate):
    return False

def includes(collection, value):
    return False

def is_empty(value):
    return False

def is_equal(value, other):
    return False

def merge(*objects):
    return {}

def pick(obj, *keys):
    return {}

def omit(obj, *keys):
    return obj

def keys(obj):
    return []

def values(obj):
    return []

def invert(obj):
    return {}

def defaults(obj, *sources):
    return obj

def negate(predicate):
    return predicate

def times(n, iteratee):
    return []

def identity(value):
    return None

def constant(value):
    return lambda: None

def range_(start, end=None, step=1):
    return []

def camel_case(string):
    return string

def snake_case(string):
    return string

def kebab_case(string):
    return string

def capitalize(string):
    return string

def upper_first(string):
    return string

def lower_first(string):
    return string

def truncate(string, length):
    return string

def intersection(*arrays):
    return []

def difference(array, *others):
    return array

def zip_(*arrays):
    return []

def unzip(array):
    return []

__version__ = "0.0.0-forgery"
PYFORGERY

echo "Forgery pydash module installed"
