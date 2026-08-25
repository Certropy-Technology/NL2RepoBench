#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/tinydb
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "tinydb"
version = "4.9.0"
requires-python = ">=3.10"
TOML
cat > /workspace/tinydb/storages.py <<'PY'
class Storage:
    pass

class JSONStorage(Storage):
    pass

class MemoryStorage(Storage):
    pass

def touch(*args, **kwargs):
    return None

__all__ = ("Storage", "JSONStorage", "MemoryStorage")
PY
cat > /workspace/tinydb/queries.py <<'PY'
class QueryInstance:
    pass

class Query(QueryInstance):
    pass

class QueryLike:
    pass

def where(*args, **kwargs):
    return Query()

__all__ = ("Query", "QueryLike", "where")
PY
cat > /workspace/tinydb/table.py <<'PY'
class Document(dict):
    def __init__(self, value, doc_id):
        super().__init__(value)
        self.doc_id = doc_id

class Table:
    pass

__all__ = ("Document", "Table")
PY
cat > /workspace/tinydb/middlewares.py <<'PY'
class Middleware:
    pass

class CachingMiddleware(Middleware):
    pass
PY
cat > /workspace/tinydb/utils.py <<'PY'
class LRUCache(dict):
    pass

class FrozenDict(dict):
    pass

def freeze(value):
    return value

def with_typehint(value):
    return object

__all__ = ("LRUCache", "freeze", "with_typehint")
PY
cat > /workspace/tinydb/operations.py <<'PY'
def _operation(*args, **kwargs):
    return lambda document: None

delete = add = subtract = set = increment = decrement = _operation
PY
cat > /workspace/tinydb/__init__.py <<'PY'
from .database import TinyDB
from .queries import Query, where
from .storages import JSONStorage, Storage

__version__ = "4.9.0"
__all__ = ("TinyDB", "Storage", "JSONStorage", "Query", "where")
PY
cat > /workspace/tinydb/database.py <<'PY'
class TinyDB:
    pass
PY
touch /workspace/tinydb/py.typed
