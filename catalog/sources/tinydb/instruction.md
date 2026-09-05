# Project Description

Build TinyDB 4.9.0, a small installable Python document database. TinyDB stores
mapping-like documents in named tables, assigns integer document IDs, supports
composable in-process queries, and persists the complete database through a
replaceable storage object. It includes in-memory and JSON-file storage, a
caching storage middleware, an LRU query cache, and reusable update operations.

The scored contract is bounded to the package, storage, query, table,
middleware, cache, and update behavior described below. It does not require a
CLI, networking, asynchronous access, schema validation, concurrency control,
third-party serialization formats, documentation tooling, or development-only
test dependencies.

# Natural Language Instruction

Create the installable `tinydb` package from an empty workspace. Implement the
document, table, query, storage, middleware, cache, and update-operation
contracts below. Preserve document IDs, storage order, cache invalidation,
copy semantics, and the stated exception behavior across modules.

# Supports

- Python 3.12 on Linux.
- An installable distribution named `tinydb`, version `4.9.0`, requiring
  Python 3.10 or newer.
- The import package `tinydb` and a `tinydb/py.typed` marker.
- No required runtime package-index dependencies.
- Installation from the repository root with
  `pip --no-deps --no-build-isolation` after the declared build backend has
  already been installed.
- No runtime network access, subprocesses, external services, or writes outside
  paths explicitly supplied by the caller.

The top-level package exposes `__version__ == "4.9.0"` and this exact
`__all__` order:

~~~python
("TinyDB", "Storage", "JSONStorage", "Query", "where")
~~~

These module-level export tuples are also part of the contract:

~~~python
tinydb.storages.__all__ == ("Storage", "JSONStorage", "MemoryStorage")
tinydb.queries.__all__ == ("Query", "QueryLike", "where")
tinydb.table.__all__ == ("Document", "Table")
tinydb.utils.__all__ == ("LRUCache", "freeze", "with_typehint")
~~~

# Project Directory Structure

```text
workspace/
├── pyproject.toml
└── tinydb/
    ├── __init__.py
    ├── database.py
    ├── middlewares.py
    ├── operations.py
    ├── queries.py
    ├── storages.py
    ├── table.py
    ├── utils.py
    └── py.typed
```

# API Usage Guide

## Storage API

### `tinydb.storages.Storage`

`Storage` is an abstract base class. Instantiating it directly raises
`TypeError`. Subclasses implement:

```python
read() -> dict[str, dict[str, object]] | None
write(data: dict[str, dict[str, object]]) -> None
close() -> None
```

`read()` returns `None` for an uninitialized storage. `close()` is an optional
no-op in the base class.

### `tinydb.storages.MemoryStorage`

```python
MemoryStorage()
```

The initial `read()` result is `None`. `write(data)` stores the supplied object
in the public `memory` attribute without serialization or copying, so the next
`read()` returns that same object. `write()` and `close()` return `None`.

### `tinydb.storages.touch`

```python
touch(path: str, create_dirs: bool) -> None
```

Create an empty file if it does not exist. Existing contents are preserved. If
`create_dirs` is true, create missing parent directories first.

### `tinydb.storages.JSONStorage`

```python
JSONStorage(
    path: str,
    create_dirs: bool = False,
    encoding: str | None = None,
    access_mode: str = "r+",
    **json_dump_options,
)
```

For a writable mode, create the file using `touch`; `create_dirs` controls
parent creation. Open the file once and keep its handle until `close()`.
`read()` returns `None` for an empty file and otherwise seeks to the beginning
and returns `json.load(handle)`. A read-only missing path raises
`FileNotFoundError`.

`write(data)` seeks to the beginning, serializes with `json.dumps(data,
**json_dump_options)`, writes, flushes, calls `fsync`, and truncates stale
trailing bytes. Options such as `ensure_ascii`, `sort_keys`, and `separators`
must therefore affect the file exactly as they affect `json.dumps`. A write
through access mode `"r"` raises `OSError` with:

```text
Cannot write to the database. Access mode is "r"
```

Modes other than `r`, `rb`, `r+`, or `rb+` emit `UserWarning` mentioning the
risk of data loss or corruption.

## Documents and Tables

### `tinydb.table.Document`

```python
Document(value: Mapping, doc_id: int)
```

`Document` is a `dict` initialized from a shallow copy of `value` and exposes
the ID separately as mutable attribute `doc_id`. The ID does not appear as a
mapping key and does not affect normal dictionary equality.

### `tinydb.table.Table`

```python
Table(
    storage: Storage,
    name: str,
    cache_size: int = 10,
    persist_empty: bool = False,
)
```

The public class customizations are `document_class = Document`,
`document_id_class = int`, `query_cache_class = LRUCache`, and
`default_query_cache_capacity = 10`. `name` and `storage` are read-only
properties. If `persist_empty=True`, construction immediately persists the
named empty table.

The storage representation is a dictionary of table names. Each table maps
string document IDs to plain document mappings. Public results convert IDs
back to `int` and documents to `document_class`.

#### Insertion and reads

```python
insert(document: Mapping) -> int
insert_multiple(documents: Iterable[Mapping]) -> list[int]
all() -> list[Document]
get(cond=None, doc_id=None, doc_ids=None) -> Document | list[Document] | None
search(cond: QueryLike) -> list[Document]
contains(cond=None, doc_id=None) -> bool
count(cond: QueryLike) -> int
```

Plain mappings receive monotonically increasing IDs beginning at 1. A
`Document` keeps its explicit `doc_id`; inserting a duplicate ID raises
`ValueError` with `Document with ID <id> already exists`. Inserting anything
that is not a `Mapping` raises `ValueError("Document is not a Mapping")`.
`insert_multiple` preserves input order and returns IDs in that order.

`all()` and iteration preserve storage order. `get(doc_id=...)` returns one
document or `None`. `get(doc_ids=...)` returns existing requested IDs in table
storage order, not request order, and silently omits missing IDs.
`get(cond)` returns the first matching document or `None`. Calling `get()`
without any selector raises
`RuntimeError("You have to pass either cond or doc_id or doc_ids")`.

`contains` gives `doc_id` precedence when supplied, otherwise checks the first
query match. Calling it without a selector raises
`RuntimeError("You have to pass either cond or doc_id")`.

#### Updates, upserts, and removals

```python
update(fields: Mapping | Callable[[MutableMapping], None], cond=None, doc_ids=None) -> list[int]
update_multiple(updates: Iterable[tuple[Mapping | Callable, QueryLike]]) -> list[int]
upsert(document: Mapping, cond=None) -> list[int]
remove(cond=None, doc_ids=None) -> list[int]
truncate() -> None
clear_cache() -> None
```

`update` merges a mapping into each selected document, or calls a transform
that mutates each selected document in place. `doc_ids` takes precedence over
`cond`; missing IDs are silently skipped. With only `cond`, matching documents
are processed in table order. With neither, all documents are updated. Return
only IDs actually updated, in processing order.

`update_multiple` visits documents in table order and, for each document,
visits update/query pairs in input order. Every matching pair is applied. Its
return list contains an ID once per applied pair, so overlapping conditions can
produce duplicate IDs.

`upsert` updates every match. If no match exists, insert the supplied mapping.
A `Document` may select its own ID without a query, updating that ID or
inserting it if absent. A plain mapping with no query raises `ValueError` whose
message explains that a query or `Document.doc_id` is required.

`remove(doc_ids=...)` and `remove(cond)` return removed IDs in processing
order and omit missing IDs. Calling `remove()` without a selector raises
`RuntimeError("Use truncate() to remove all documents")`. `truncate()` empties
the table and resets automatic ID allocation, so its next plain insertion gets
ID 1.

Every table write rewrites the complete storage state and clears that table's
query cache.

## Database API

### `tinydb.database.TinyDB`

```python
TinyDB(*storage_args, storage=JSONStorage, **storage_kwargs)
table(name: str, **table_kwargs) -> Table
tables() -> set[str]
drop_table(name: str) -> None
drop_tables() -> None
close() -> None
```

Construct the selected storage with all positional arguments and all keywords
except `storage`. `storage` exposes that instance. The default table name is
`"_default"`; unknown attributes such as `insert`, `search`, and `all` forward
to that table. `len(db)` and iteration also forward to it.

`table(name)` caches and returns one `Table` instance per name. `tables()` is
derived from storage state, so merely accessing a table does not persist its
name unless `persist_empty=True` or a write occurs. `drop_table` is a no-op for
an absent table, removes the stored table when present, and forgets its cached
`Table` instance. `drop_tables` writes `{}` and forgets every cached table.

`TinyDB` is a context manager. `__enter__` returns the database. On normal or
exceptional exit, `__exit__` closes an open database but does not suppress the
exception. `close()` marks the database closed and forwards to storage every
time it is directly called; `__exit__` avoids a duplicate close after an
earlier close.

## Query API

### Builders and query instances

```python
Query()
where(key: str) -> Query
```

Attribute and item access append mapping-key path components. For example,
`Query().profile["name"] == "Ada"` resolves nested mappings. `where("name")`
is shorthand for `Query()["name"]`. A missing key or a `TypeError` while
resolving the path makes a generated query return `False`. Calling a bare
`Query()` raises `RuntimeError("Empty query was evaluated")`; generating a
path-dependent test from a bare query raises `ValueError("Query has no path")`.
The builder representation is `Query()`.

A generated `QueryInstance` is callable with a mapping and supports `&`, `|`,
and `~`. AND and OR identity/hash descriptions are commutative. Query equality
compares stable query descriptions. `is_cacheable()` reports whether a stable
description exists.

Comparisons `==`, `!=`, `<`, `<=`, `>`, and `>=` apply to the resolved value.
Additional methods are:

```python
exists() -> QueryInstance
matches(regex: str, flags: int = 0) -> QueryInstance
search(regex: str, flags: int = 0) -> QueryInstance
test(func: Callable, *args) -> QueryInstance
any(cond: QueryInstance | list) -> QueryInstance
all(cond: QueryInstance | list) -> QueryInstance
one_of(items: list) -> QueryInstance
fragment(document: Mapping) -> QueryInstance
noop() -> QueryInstance
map(fn: Callable) -> Query
```

`matches` requires a string and uses `re.match`; `search` requires a string and
uses `re.search`. Both pass flags through. `test` calls
`func(resolved_value, *args)`. Lists, tuples, sets, and nested dictionaries in
query arguments are recursively frozen for stable hashing. If a complete
query description still contains an unhashable value, the query is valid but
uncacheable.

For `any(query)` and `all(query)`, evaluate the child query against elements of
the resolved iterable. For a list argument, `any` checks whether at least one
resolved element occurs in that list, while `all` checks whether every
argument item occurs in the resolved iterable. `one_of` tests the resolved
value for membership.

`fragment(mapping)` checks that every supplied key/value pair occurs at the
resolved mapping and may be called on a bare `Query`. `noop()` always returns
true and is cacheable. `map(fn)` appends a callable path transformation and
always marks the resulting query uncacheable.

## Update Operations

`tinydb.operations` provides transform factories suitable for `Table.update`:

```python
delete(field: str)     # del document[field]
add(field: str, n)     # document[field] += n
subtract(field: str, n)# document[field] -= n
set(field: str, value) # document[field] = value
increment(field: str)  # document[field] += 1
decrement(field: str)  # document[field] -= 1
```

Each factory returns a callable that mutates one mutable mapping in place and
returns `None`. Ordinary Python key and arithmetic errors propagate.

## Middleware API

### `tinydb.middlewares.Middleware`

```python
Middleware(storage_class)
middleware(*args, **kwargs) -> middleware
```

Calling a middleware constructs the wrapped storage with the supplied
arguments, stores it as `middleware.storage`, and returns the middleware
itself. Unknown attributes forward to the wrapped storage. Middleware objects
may be nested; calling the outer middleware initializes each layer.

### `tinydb.middlewares.CachingMiddleware`

`CachingMiddleware` starts with `cache = None`, modified count zero, and class
constant `WRITE_CACHE_SIZE = 1000`. `read()` returns the cache; while the cache
is `None`, every read delegates again to storage. `write(data)` replaces the
cache and increments the modified count without immediately writing. At the
threshold it calls `flush()`.

`flush()` writes the latest cached object once only when the modified count is
positive, then resets the count. `close()` flushes and then closes the wrapped
storage. Thus a TinyDB context using `CachingMiddleware(JSONStorage)` may leave
the JSON file empty inside the context but persists valid data and closes the
file on exit.

## Cache and Freezing Utilities

### `tinydb.utils.LRUCache`

```python
LRUCache(capacity: int | None = None)
```

This mutable mapping uses insertion/access order from least to most recently
used. `lru` returns the key order and `length` returns its size. Getting an
existing non-`None` value moves the key to the newest end. Setting an existing
key, including one currently holding a falsy value, updates and moves it.
Adding beyond a finite capacity evicts the oldest key. `capacity=None` is
unlimited. Deletion, iteration, membership, and `clear()` follow mutable
mapping behavior.

`get(key, default)` returns the default when the stored value is `None`.
Consequently `cache[key]` raises `KeyError` both for an absent key and for a
key whose stored value is `None`.

### `tinydb.utils.freeze` and `FrozenDict`

```python
freeze(value) -> hashable_value
```

Recursively convert dictionaries to `FrozenDict`, lists and tuples to tuples,
and sets to frozensets; return other values unchanged. `FrozenDict` hashes its
sorted items. Item assignment/deletion, `clear`, `setdefault`, `popitem`,
`update`, and `pop` raise `TypeError("object is immutable")`.

# Implementation Notes

- Preserve document and table order; do not sort database records implicitly.
- JSON file operations must use only the caller-provided path. Temporary files
  used internally must remain under the operating system temporary directory.
- Keep trusted expected behavior out of the package itself. The implementation
  should be an ordinary reusable library, not a special-case response table.
- Query caching assumes cacheable custom query objects have stable `__hash__`
  and deterministic calls. Uncacheable queries are evaluated on every search.
- A cached `search` returns a fresh result list, but the `Document` objects in
  it are shared with the cache. Mutating one is visible to the next identical
  cached search until a table write or `clear_cache()` invalidates the cache.

# Examples

```python
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

db = TinyDB(storage=MemoryStorage)
assert db.insert({"name": "Ada"}) == 1
assert db.all()[0]["name"] == "Ada"
```

```python
from tinydb import Query

assert db.search(Query().name == "Ada")[0].doc_id == 1
```

# Error Handling and Boundary Conditions

Missing selectors raise the specified `RuntimeError`. Duplicate document IDs
and non-mapping documents raise `ValueError`. JSON storage must truncate stale
trailing bytes and must never write outside the path supplied by its caller.
