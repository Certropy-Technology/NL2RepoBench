#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/funcy
cat > /workspace/setup.py <<'PY'
from setuptools import setup
setup(name="funcy", version="2.0", packages=["funcy"])
PY
cat > /workspace/funcy/__init__.py <<'PY'
__all__ = [
    "autocurry", "cache", "cached_property", "chunks", "compact", "compose",
    "curry", "distinct", "drop", "flatten", "group_by", "keep", "lfilter",
    "lmap", "memoize", "merge", "merge_with", "once", "pairwise", "select",
    "take", "update_in", "walk",
]

def _identity(value, *args, **kwargs):
    return value

def _decorator(function=None, **kwargs):
    return function if function is not None else (lambda wrapped: wrapped)

autocurry = compose = curry = _identity
cache = memoize = _decorator
cached_property = property
chunks = distinct = drop = flatten = group_by = keep = pairwise = take = lambda *args, **kwargs: iter(())
compact = lfilter = lmap = merge = merge_with = select = walk = lambda *args, **kwargs: []
once = _decorator
update_in = lambda value, *args, **kwargs: value
PY
for module in calc colls decorators debug flow funcolls funcmakers funcs objects primitives seqs strings tree types; do
    cat > "/workspace/funcy/$module.py" <<'PY'
__all__ = []
PY
done
