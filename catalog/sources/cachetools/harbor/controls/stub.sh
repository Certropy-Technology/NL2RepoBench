#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/cachetools
cat > /workspace/pyproject.toml <<'PYPROJECT'
[build-system]
requires = []
build-backend = "setuptools.build_meta:__legacy__"

[project]
name = "cachetools"
version = "7.1.7"
requires-python = ">=3.10"

[tool.setuptools]
package-dir = {"" = "src"}
[tool.setuptools.packages.find]
where = ["src"]
PYPROJECT
cat > /workspace/src/cachetools/__init__.py <<'PACKAGE'
__version__ = "7.1.7"
__all__ = ("Cache", "FIFOCache", "LFUCache", "LRUCache", "RRCache", "TLRUCache", "TTLCache", "cached", "cachedmethod")
class Cache(dict):
    maxsize = 0
    currsize = 0
    @staticmethod
    def getsizeof(value): return 1
class FIFOCache(Cache): pass
class LFUCache(Cache): pass
class LRUCache(Cache): pass
class RRCache(Cache): pass
class TLRUCache(Cache): pass
class TTLCache(Cache): pass
def cached(*args, **kwargs): return lambda function: function
def cachedmethod(*args, **kwargs): return lambda function: function
PACKAGE
cat > /workspace/src/cachetools/func.py <<'FUNC'
__all__ = ("fifo_cache", "lfu_cache", "lru_cache", "rr_cache", "ttl_cache")
def _decorator(*args, **kwargs): return lambda function: function
fifo_cache = lfu_cache = lru_cache = rr_cache = ttl_cache = _decorator
FUNC
cat > /workspace/src/cachetools/keys.py <<'KEYS'
__all__ = ("hashkey", "methodkey", "typedkey", "typedmethodkey")
def hashkey(*args, **kwargs): return args
def methodkey(_self, *args, **kwargs): return args
def typedkey(*args, **kwargs): return args
def typedmethodkey(_self, *args, **kwargs): return args
KEYS
