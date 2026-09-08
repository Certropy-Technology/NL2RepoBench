# More Itertools

## Project Description

`more-itertools` is a Python library providing advanced iteration utilities beyond the standard `itertools`. It offers over 150 functions for grouping, windowing, filtering, selecting, transforming, and analyzing sequences.

## Natural Language Instruction

Build a Python package `more-itertools` (install name `more_itertools`) that provides advanced iteration utilities. Must export all public functions from `more_itertools.more` and `more_itertools.recipes` through top-level import.

Key functions: chunked, batched, sliced, distribute, divide, split_at/before/after/into, peekable, seekable, spy, windowed, pairwise, first, last, one, nth, take, tail, ilen, all_equal, flatten, interleave, roundrobin, dotproduct, powerset.

## Environment Configuration

- Python 3.12
- Build: flit_core >=3.12,<4
- No runtime dependencies
- No network access

## Project Directory Structure

```
workspace/
├── pyproject.toml
├── LICENSE
└── more_itertools/
    ├── __init__.py
    ├── more.py
    └── recipes.py
```

## API Usage Guide

See full instruction for complete API documentation of all 174 functions across grouping, windowing, selecting, summarizing, combining, mathematical, and combinatorial categories.
