#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
mkdir -p /workspace/cachecontrol/caches
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = []
build-backend = "setuptools.build_meta:__legacy__"
[project]
name = "CacheControl"
version = "0.14.4"
dependencies = ["requests>=2.16.0", "msgpack>=0.5.2,<2.0.0"]
[tool.setuptools.packages.find]
where = ["."]
include = ["cachecontrol*"]
EOF
cat > /workspace/cachecontrol/__init__.py <<'EOF'
__author__ = "Eric Larson"
__email__ = "eric@ionrock.org"
__version__ = "0.14.4"
__all__ = ["__author__", "__email__", "__version__", "CacheControlAdapter", "CacheController", "CacheControl"]
class CacheControlAdapter: pass
class CacheController: pass
def CacheControl(session, cache=None, cache_etags=True, serializer=None, heuristic=None): return session
EOF
cat > /workspace/cachecontrol/cache.py <<'EOF'
class BaseCache:
    def get(self, key): raise NotImplementedError
    def set(self, key, value, expires=None): raise NotImplementedError
    def delete(self, key): raise NotImplementedError
    def close(self): pass
class DictCache(BaseCache):
    def __init__(self, init_dict=None): self.data = init_dict or {}
    def get(self, key): return self.data.get(key)
    def set(self, key, value, expires=None): self.data[key] = value
    def delete(self, key): self.data.pop(key, None)
class SeparateBodyBaseCache(BaseCache): pass
EOF
cat > /workspace/cachecontrol/controller.py <<'EOF'
def parse_uri(uri): return (None, None, uri, None, None)
class CacheController:
    def __init__(self, *args, **kwargs): pass
    @classmethod
    def cache_url(cls, uri): return uri
    def parse_cache_control(self, headers): return {}
EOF
cat > /workspace/cachecontrol/serialize.py <<'EOF'
class Serializer:
    serde_version = "4"
    def dumps(self, request, response, body=None): return b"cc=4,"
    def loads(self, request, data, body_file=None): return None
EOF
cat > /workspace/cachecontrol/heuristics.py <<'EOF'
class BaseHeuristic:
    def apply(self, response): return response
class OneDayCache(BaseHeuristic): pass
class ExpiresAfter(BaseHeuristic): pass
class LastModified(BaseHeuristic): pass
EOF
cat > /workspace/cachecontrol/adapter.py <<'EOF'
class CacheControlAdapter: pass
EOF
cat > /workspace/cachecontrol/caches/__init__.py <<'EOF'
from cachecontrol.cache import DictCache
EOF
cat > /workspace/cachecontrol/caches/file_cache.py <<'EOF'
class FileCache: pass
class SeparateBodyFileCache: pass
def url_to_file_path(url, filecache): return ""
EOF
