#!/bin/bash
set -euo pipefail

echo "[control:stub] Creating stub implementation with package structure but non-functional code"

cd /workspace

# Create pyproject.toml
cat > pyproject.toml << 'PYPROJECT'
[project]
name = "more-itertools"
version = "11.1.0"
description = "More routines for operating on iterables, beyond itertools"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}

[build-system]
requires = ["flit_core >=3.2,<4"]
build-backend = "flit_core.buildapi"
PYPROJECT

# Create README.md
cat > README.md << 'README'
# more-itertools stub

This is a stub implementation with correct package structure but non-functional code.
README

# Create more_itertools package
mkdir -p more_itertools

# Create __init__.py with stub functions that raise NotImplementedError
cat > more_itertools/__init__.py << 'INIT'
"""Stub implementation of more-itertools."""

__version__ = "11.1.0"

# Grouping
def chunked(iterable, n, strict=False):
    raise NotImplementedError("Stub implementation")

def batched(iterable, n):
    raise NotImplementedError("Stub implementation")

def sliced(seq, n):
    raise NotImplementedError("Stub implementation")

def distribute(n, iterable):
    raise NotImplementedError("Stub implementation")

def divide(n, iterable):
    raise NotImplementedError("Stub implementation")

def split_at(iterable, pred, maxsplit=-1, keep_separator=False):
    raise NotImplementedError("Stub implementation")

def split_before(iterable, pred, maxsplit=-1):
    raise NotImplementedError("Stub implementation")

def split_after(iterable, pred, maxsplit=-1):
    raise NotImplementedError("Stub implementation")

def split_into(iterable, sizes):
    raise NotImplementedError("Stub implementation")

def partition(pred, iterable):
    raise NotImplementedError("Stub implementation")

def unzip(iterable):
    raise NotImplementedError("Stub implementation")

def grouper(iterable, n, fillvalue=None):
    raise NotImplementedError("Stub implementation")

# Lookahead and Lookback
def spy(iterable, n=1):
    raise NotImplementedError("Stub implementation")

class peekable:
    def __init__(self, iterable):
        raise NotImplementedError("Stub implementation")
    def peek(self, default=None):
        raise NotImplementedError("Stub implementation")

class seekable:
    def __init__(self, iterable):
        raise NotImplementedError("Stub implementation")
    def seek(self, index):
        raise NotImplementedError("Stub implementation")

# Windowing
def windowed(seq, n, fillvalue=None, step=1):
    raise NotImplementedError("Stub implementation")

def pairwise(iterable):
    raise NotImplementedError("Stub implementation")

def triplewise(iterable):
    raise NotImplementedError("Stub implementation")

def sliding_window(iterable, n):
    raise NotImplementedError("Stub implementation")

def stagger(iterable, offsets=(-1, 0, 1), longest=False, fillvalue=None):
    raise NotImplementedError("Stub implementation")

# Selecting
def first(iterable, default=None):
    raise NotImplementedError("Stub implementation")

def last(iterable, default=None):
    raise NotImplementedError("Stub implementation")

def one(iterable, too_short=None, too_long=None):
    raise NotImplementedError("Stub implementation")

def only(iterable, default=None, too_long=None):
    raise NotImplementedError("Stub implementation")

def nth(iterable, n, default=None):
    raise NotImplementedError("Stub implementation")

def take(n, iterable):
    raise NotImplementedError("Stub implementation")

def tail(n, iterable):
    raise NotImplementedError("Stub implementation")

def strictly_n(iterable, n, too_short=None, too_long=None):
    raise NotImplementedError("Stub implementation")

def strip(iterable, pred):
    raise NotImplementedError("Stub implementation")

def lstrip(iterable, pred):
    raise NotImplementedError("Stub implementation")

def rstrip(iterable, pred):
    raise NotImplementedError("Stub implementation")

def filter_map(func, iterable):
    raise NotImplementedError("Stub implementation")

def unique_everseen(iterable, key=None):
    raise NotImplementedError("Stub implementation")

def unique_justseen(iterable, key=None):
    raise NotImplementedError("Stub implementation")

def unique(iterable, key=None, reverse=False):
    raise NotImplementedError("Stub implementation")

# Summarizing
def ilen(iterable):
    raise NotImplementedError("Stub implementation")

def all_equal(iterable, key=None):
    raise NotImplementedError("Stub implementation")

def all_unique(iterable, key=None):
    raise NotImplementedError("Stub implementation")

def is_sorted(iterable, key=None, reverse=False, strict=False):
    raise NotImplementedError("Stub implementation")

def exactly_n(iterable, n, predicate=bool):
    raise NotImplementedError("Stub implementation")

def quantify(iterable, pred=bool):
    raise NotImplementedError("Stub implementation")

def first_true(iterable, default=None, pred=None):
    raise NotImplementedError("Stub implementation")

def argmin(iterable, key=None, default=None):
    raise NotImplementedError("Stub implementation")

def argmax(iterable, key=None, default=None):
    raise NotImplementedError("Stub implementation")

def minmax(iterable, key=None, default=None):
    raise NotImplementedError("Stub implementation")

def consecutive_groups(iterable, ordering=lambda x: x):
    raise NotImplementedError("Stub implementation")

def run_length(iterable):
    raise NotImplementedError("Stub implementation")

# Combining
def flatten(listOfLists):
    raise NotImplementedError("Stub implementation")

def collapse(iterable, base_type=None, levels=None):
    raise NotImplementedError("Stub implementation")

def interleave(*iterables):
    raise NotImplementedError("Stub implementation")

def interleave_longest(*iterables, fillvalue=None):
    raise NotImplementedError("Stub implementation")

def roundrobin(*iterables):
    raise NotImplementedError("Stub implementation")

def prepend(value, iterable):
    raise NotImplementedError("Stub implementation")

def value_chain(*args):
    raise NotImplementedError("Stub implementation")

# Mathematical
def dotproduct(vec1, vec2):
    raise NotImplementedError("Stub implementation")

def sum_of_squares(it):
    raise NotImplementedError("Stub implementation")

def transpose(it):
    raise NotImplementedError("Stub implementation")

def polynomial_eval(coefficients, x):
    raise NotImplementedError("Stub implementation")

def convolve(signal, kernel):
    raise NotImplementedError("Stub implementation")

def matmul(m1, m2):
    raise NotImplementedError("Stub implementation")

# Combinatorial
def powerset(iterable):
    raise NotImplementedError("Stub implementation")

def circular_shifts(iterable):
    raise NotImplementedError("Stub implementation")

def partitions(n, m=None):
    raise NotImplementedError("Stub implementation")

def set_partitions(iterable, k=None):
    raise NotImplementedError("Stub implementation")

# Utility
def consume(iterator, n=None):
    raise NotImplementedError("Stub implementation")

def iter_except(func, exception, first=None):
    raise NotImplementedError("Stub implementation")

def repeatfunc(func, times=None, *args):
    raise NotImplementedError("Stub implementation")

def side_effect(func, iterable, chunk_size=None, before=None, after=None):
    raise NotImplementedError("Stub implementation")

def always_iterable(obj, base_type=(str, bytes)):
    raise NotImplementedError("Stub implementation")

class countable:
    def __init__(self, iterable):
        raise NotImplementedError("Stub implementation")
    @property
    def items_seen(self):
        raise NotImplementedError("Stub implementation")
INIT

# Create py.typed marker
touch more_itertools/py.typed

echo "[control:stub] Stub implementation created with correct package structure"
