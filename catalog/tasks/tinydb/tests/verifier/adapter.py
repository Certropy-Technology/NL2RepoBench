from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import tempfile
from typing import Any, Callable
import warnings


CANDIDATE_SITE = Path(
    __import__("os").environ.get("NL2REPO_TINYDB_CANDIDATE_SITE", "/tmp/candidate-site")
)
sys.path.insert(0, str(CANDIDATE_SITE))
dependency_site = __import__("os").environ.get("NL2REPO_CANDIDATE_DEPENDENCIES")
if dependency_site:
    sys.path.insert(1, dependency_site)

import tinydb
from tinydb import JSONStorage, Query, Storage, TinyDB, where
from tinydb.middlewares import CachingMiddleware, Middleware
from tinydb.operations import add, decrement, delete, increment, set, subtract
from tinydb.queries import QueryInstance
from tinydb.storages import MemoryStorage, touch
from tinydb.table import Document, Table
from tinydb.utils import FrozenDict, LRUCache, freeze


def error_details(call: Callable[..., Any], *args: Any, **kwargs: Any) -> dict[str, Any]:
    try:
        call(*args, **kwargs)
    except Exception as exc:
        return {"type": type(exc).__name__, "message": str(exc)}
    return {"type": None, "message": None}


def docs(values: Any) -> list[dict[str, Any]]:
    return [{"doc_id": value.doc_id, "value": dict(value)} for value in values]


class RecordingStorage(Storage):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.data = None
        self.init = {"args": list(args), "kwargs": kwargs}
        self.reads = 0
        self.writes: list[Any] = []
        self.close_count = 0
        self.marker = "forwarded"

    def read(self):
        self.reads += 1
        return self.data

    def write(self, data):
        self.data = data
        self.writes.append(data)

    def close(self):
        self.close_count += 1


def package_surface() -> dict[str, Any]:
    import tinydb.operations as operations
    import tinydb.queries as queries
    import tinydb.storages as storages
    import tinydb.table as table
    import tinydb.utils as utils

    return {
        "version": tinydb.__version__,
        "all": list(tinydb.__all__),
        "module_all": {
            "queries": list(queries.__all__),
            "storages": list(storages.__all__),
            "table": list(table.__all__),
            "utils": list(utils.__all__),
        },
        "operations": [
            callable(getattr(operations, name))
            for name in ("delete", "add", "subtract", "set", "increment", "decrement")
        ],
        "classes": [
            TinyDB.__name__, Storage.__name__, JSONStorage.__name__,
            Query.__name__, Document.__name__, Table.__name__,
            Middleware.__name__, CachingMiddleware.__name__, LRUCache.__name__,
        ],
    }


def storage_memory() -> dict[str, Any]:
    storage = MemoryStorage()
    initial = storage.read()
    payload = {"items": {"1": {"value": [1, 2]}}}
    write_result = storage.write(payload)
    observed = storage.read()
    close_result = storage.close()
    return {
        "initial": initial,
        "observed": observed,
        "same_object": observed is payload,
        "write_result": write_result,
        "close_result": close_result,
    }


def storage_json() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="tinydb-storage-") as temporary:
        path = Path(temporary) / "nested" / "db.json"
        storage = JSONStorage(
            str(path), create_dirs=True, encoding="utf-8", ensure_ascii=False,
            sort_keys=True, separators=(",", ":")
        )
        initial = storage.read()
        first = {"beta": {"2": {"text": "café"}}, "alpha": {"1": {"n": 7}}}
        storage.write(first)
        first_raw = path.read_text(encoding="utf-8")
        storage.write({"x": {}})
        second_raw = path.read_text(encoding="utf-8")
        second = storage.read()
        storage.close()
        return {
            "parent_created": path.parent.is_dir(),
            "initial": initial,
            "first_raw": first_raw,
            "second_raw": second_raw,
            "second": second,
            "closed": storage._handle.closed,
        }


def storage_json_modes() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="tinydb-modes-") as temporary:
        root = Path(temporary)
        path = root / "db.json"
        path.write_text('{"t":{"1":{"v":1}}}', encoding="utf-8")
        readonly = JSONStorage(str(path), access_mode="r", encoding="utf-8")
        loaded = readonly.read()
        write_error = error_details(readonly.write, {"t": {}})
        readonly.close()
        try:
            JSONStorage(str(root / "missing.json"), access_mode="r")
        except Exception as exc:
            missing_error = {
                "type": type(exc).__name__,
                "errno": getattr(exc, "errno", None),
            }
        else:
            missing_error = {"type": None, "errno": None}
        touched = root / "touch.txt"
        touched.write_text("keep", encoding="utf-8")
        touch(str(touched), create_dirs=False)
        warning_path = root / "warning.json"
        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter("always")
            warning_storage = JSONStorage(str(warning_path), access_mode="w+")
            warning_storage.close()
        return {
            "loaded": loaded,
            "write_error": write_error,
            "missing_error": missing_error,
            "touch_preserved": touched.read_text(encoding="utf-8"),
            "warning_type": type(captured[0].message).__name__ if captured else None,
            "warning_mentions_corruption": "corruption" in str(captured[0].message) if captured else False,
        }


def storage_contract() -> dict[str, Any]:
    abstract_error = error_details(Storage)
    storage = RecordingStorage("path", mode="safe")
    initial = storage.read()
    storage.write({"table": {}})
    observed = storage.read()
    storage.close()
    return {
        "abstract_error": abstract_error["type"],
        "init": storage.init,
        "initial": initial,
        "observed": observed,
        "reads": storage.reads,
        "write_count": len(storage.writes),
        "close_count": storage.close_count,
    }


def query_comparisons() -> dict[str, Any]:
    records = [{"n": 2}, {"n": 3}, {"n": 4}, {"x": 3}]
    conditions = {
        "eq": where("n") == 3,
        "ne": where("n") != 3,
        "lt": where("n") < 3,
        "le": where("n") <= 3,
        "gt": where("n") > 3,
        "ge": where("n") >= 3,
    }
    return {name: [condition(record) for record in records] for name, condition in conditions.items()}


def query_logic() -> dict[str, Any]:
    left = where("a") == 1
    right = where("b") == 2
    records = [{"a": 1, "b": 2}, {"a": 1, "b": 0}, {"a": 0, "b": 2}, {}]
    return {
        "and": [(left & right)(record) for record in records],
        "or": [(left | right)(record) for record in records],
        "not": [(~left)(record) for record in records],
        "commutative_equality": (left & right) == (right & left),
        "commutative_hash": hash(left | right) == hash(right | left),
        "cacheable": [(left & right).is_cacheable(), (~left).is_cacheable()],
    }


def query_paths() -> dict[str, Any]:
    nested = Query().profile["first"] == "Ada"
    mapped = where("name").map(str.casefold) == "alice"
    records = [
        {"profile": {"first": "Ada"}, "name": "ALICE"},
        {"profile": {}, "name": "Bob"},
        {"profile": None, "name": 3},
        {},
    ]
    return {
        "nested": [nested(record) for record in records],
        "mapped": [mapped(record) for record in records],
        "mapped_cacheable": mapped.is_cacheable(),
        "where_repr": repr(where("field")),
    }


def query_regex() -> dict[str, Any]:
    records = [{"s": "Alpha-42"}, {"s": "xx ALPHA yy"}, {"s": 42}, {}]
    matched = where("s").matches(r"alpha-\d+", flags=re.IGNORECASE)
    searched = where("s").search(r"alpha", flags=re.IGNORECASE)
    return {
        "matches": [matched(record) for record in records],
        "search": [searched(record) for record in records],
    }


def query_collections() -> dict[str, Any]:
    records = [
        {"items": [{"v": 1}, {"v": 2}], "tags": [1, 2, 3], "choice": "b"},
        {"items": [{"v": 0}], "tags": [2], "choice": "x"},
        {"items": "abc", "tags": [], "choice": 1},
        {},
    ]
    conditions = {
        "any_query": where("items").any(where("v") == 2),
        "all_query": where("items").all(where("v") > 0),
        "any_values": where("tags").any([3, 9]),
        "all_values": where("tags").all([1, 3]),
        "one_of": where("choice").one_of(["a", "b", 1]),
    }
    return {name: [condition(record) for record in records] for name, condition in conditions.items()}


def query_fragment() -> dict[str, Any]:
    records = [
        {"name": "Ada", "meta": {"active": True}, "extra": 1},
        {"name": "Ada", "meta": {"active": False}},
        {"name": "Bob"},
    ]
    fragment = Query().fragment({"name": "Ada", "meta": {"active": True}})
    nested = where("meta").fragment({"active": True})
    exists = where("extra").exists()
    noop = Query().noop()
    return {
        "fragment": [fragment(record) for record in records],
        "nested": [nested(record) for record in records],
        "exists": [exists(record) for record in records],
        "noop": [noop(record) for record in records],
    }


def query_custom_cacheability() -> dict[str, Any]:
    def divisible(value: int, divisor: int) -> bool:
        return value % divisor == 0

    first = where("n").test(divisible, 2)
    second = where("n").test(divisible, 2)

    class Unhashable:
        __hash__ = None

        def __eq__(self, other: object) -> bool:
            return self is other

    uncacheable = where("value") == Unhashable()
    frozen_arg = where("n").test(lambda value, choices: value in choices, [2, 4])
    return {
        "values": [first({"n": value}) for value in (2, 3, 4)],
        "equal": first == second,
        "same_hash": hash(first) == hash(second),
        "cacheable": first.is_cacheable(),
        "uncacheable": uncacheable.is_cacheable(),
        "frozen_argument": [frozen_arg({"n": value}) for value in (2, 3, 4)],
    }


def query_errors() -> dict[str, Any]:
    return {
        "empty_evaluation": error_details(Query(), {}),
        "missing_path": error_details(Query().exists),
        "missing_path_comparison": error_details(lambda: Query() == 1),
    }


def table_insert() -> dict[str, Any]:
    db = TinyDB(storage=MemoryStorage)
    first = db.insert({"name": "Ada"})
    second = db.insert({"name": "Bob"})
    explicit = db.insert(Document({"name": "Grace"}, doc_id=10))
    following = db.insert({"name": "Linus"})
    return {
        "ids": [first, second, explicit, following],
        "all": docs(db.all()),
        "length": len(db),
        "raw": db.storage.read(),
    }


def table_insert_multiple() -> dict[str, Any]:
    db = TinyDB(storage=MemoryStorage)
    first = db.insert_multiple([{"v": 1}, {"v": 2}])
    second = db.insert_multiple([Document({"v": 8}, 8), {"v": 3}])
    duplicate = error_details(db.insert, Document({"v": 9}, 8))
    invalid = error_details(db.insert_multiple, [{"ok": True}, ["not", "mapping"]])
    return {
        "first": first,
        "second": second,
        "duplicate": duplicate,
        "invalid": invalid,
        "all": docs(db.all()),
    }


def table_get() -> dict[str, Any]:
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{"v": 1}, {"v": 2}, {"v": 3}])
    by_id = db.get(doc_id=2)
    by_ids = db.get(doc_ids=[3, 99, 1])
    by_query = db.get(where("v") > 1)
    return {
        "by_id": docs([by_id]) if by_id else [],
        "by_ids": docs(by_ids),
        "by_query": docs([by_query]) if by_query else [],
        "missing": db.get(doc_id=99),
    }


def table_search() -> dict[str, Any]:
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{"v": 3}, {"v": 1}, {"v": 2}, {"v": 4}])
    condition = (where("v") >= 2) & (where("v") < 4)
    return {
        "search": docs(db.search(condition)),
        "count": db.count(where("v") >= 3),
        "contains_query": db.contains(where("v") == 1),
        "contains_id": db.contains(doc_id=4),
        "contains_missing": db.contains(doc_id=9),
        "iteration": docs(list(db)),
    }


def table_update_mapping() -> dict[str, Any]:
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{"group": "a", "n": 1}, {"group": "b", "n": 2}, {"group": "a", "n": 3}])
    matched = db.update({"flag": True}, where("group") == "a")
    selected = db.update({"selected": True}, doc_ids=[3, 99, 2])
    all_ids = db.update({"all": "yes"})
    return {"matched": matched, "selected": selected, "all_ids": all_ids, "all": docs(db.all())}


def table_update_operations() -> dict[str, Any]:
    db = TinyDB(storage=MemoryStorage)
    db.insert({"n": 2, "m": 10, "text": "a", "drop": 1})
    affected = [
        db.update(add("n", 3)),
        db.update(subtract("m", 4)),
        db.update(increment("n")),
        db.update(decrement("m")),
        db.update(set("text", "z")),
        db.update(delete("drop")),
    ]
    return {"affected": affected, "document": docs(db.all())}


def table_update_multiple() -> dict[str, Any]:
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{"kind": "a", "n": 1}, {"kind": "b", "n": 2}, {"kind": "a", "n": 3}])
    affected = db.update_multiple([
        ({"first": True}, where("kind") == "a"),
        (increment("n"), where("n") >= 2),
    ])
    return {"affected": affected, "all": docs(db.all())}


def table_remove() -> dict[str, Any]:
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{"v": 1}, {"v": 2}, {"v": 3}, {"v": 4}])
    by_query = db.remove(where("v") <= 2)
    by_ids = db.remove(doc_ids=[4, 99, 3])
    return {"by_query": by_query, "by_ids": by_ids, "remaining": docs(db.all())}


def table_upsert() -> dict[str, Any]:
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{"kind": "a", "n": 1}, {"kind": "a", "n": 2}])
    updated = db.upsert({"flag": True}, where("kind") == "a")
    inserted = db.upsert({"kind": "b", "n": 3}, where("kind") == "b")
    explicit_insert = db.upsert(Document({"kind": "c"}, 10))
    explicit_update = db.upsert(Document({"kind": "c", "flag": True}, 10))
    return {
        "updated": updated,
        "inserted": inserted,
        "explicit_insert": explicit_insert,
        "explicit_update": explicit_update,
        "all": docs(db.all()),
    }


def table_truncate_persist() -> dict[str, Any]:
    db = TinyDB(storage=MemoryStorage)
    table = db.table("items")
    table.insert_multiple([{"v": 1}, {"v": 2}])
    table.truncate()
    reset_id = table.insert({"v": 3})
    empty = db.table("empty", persist_empty=True)
    return {
        "reset_id": reset_id,
        "items": docs(table.all()),
        "empty_length": len(empty),
        "tables": sorted(db.tables()),
        "raw": db.storage.read(),
    }


def table_errors() -> dict[str, Any]:
    db = TinyDB(storage=MemoryStorage)
    return {
        "insert": error_details(db.insert, ["not", "mapping"]),
        "get": error_details(db.get),
        "contains": error_details(db.contains),
        "remove": error_details(db.remove),
        "upsert": error_details(db.upsert, {"v": 1}),
    }


def database_tables() -> dict[str, Any]:
    db = TinyDB(storage=MemoryStorage)
    alpha = db.table("alpha")
    same = db.table("alpha") is alpha
    alpha.insert({"v": 1})
    db.table("beta", persist_empty=True)
    before = sorted(db.tables())
    db.drop_table("missing")
    db.drop_table("alpha")
    after_one = sorted(db.tables())
    recreated = db.table("alpha") is alpha
    db.drop_tables()
    return {
        "same_instance": same,
        "before": before,
        "after_one": after_one,
        "recreated_is_old": recreated,
        "after_all": sorted(db.tables()),
        "raw": db.storage.read(),
    }


def database_default() -> dict[str, Any]:
    db = TinyDB(storage=MemoryStorage)
    inserted = db.insert({"v": 1})
    default = db.table(db.default_table_name)
    return {
        "inserted": inserted,
        "name": default.name,
        "same_storage": default.storage is db.storage,
        "length": len(db),
        "iterated": docs(list(db)),
        "all": docs(db.all()),
        "tables": sorted(db.tables()),
    }


def database_json_persistence() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="tinydb-persist-") as temporary:
        path = Path(temporary) / "db.json"
        with TinyDB(str(path), ensure_ascii=False, sort_keys=True) as db:
            ids = db.insert_multiple([{"name": "café"}, {"name": "Ada"}])
            db.table("other").insert({"v": 3})
        raw = json.loads(path.read_text(encoding="utf-8"))
        with TinyDB(str(path), encoding="utf-8") as reopened:
            observed = docs(reopened.all())
            tables = sorted(reopened.tables())
        return {"ids": ids, "raw": raw, "observed": observed, "tables": tables}


def database_context() -> dict[str, Any]:
    holder: dict[str, RecordingStorage] = {}

    class CapturingStorage(RecordingStorage):
        def __init__(self):
            super().__init__()
            holder["storage"] = self

    try:
        with TinyDB(storage=CapturingStorage) as db:
            db.insert({"v": 1})
            raise ValueError("body-error")
    except Exception as exc:
        propagated = {"type": type(exc).__name__, "message": str(exc)}
    db.close()
    return {
        "propagated": propagated,
        "opened": db._opened,
        "close_count": holder["storage"].close_count,
    }


def middleware_forwarding() -> dict[str, Any]:
    middleware = Middleware(RecordingStorage)
    returned = middleware("path", mode="safe")
    middleware.write({"x": {}})
    nested = Middleware(Middleware(RecordingStorage))
    nested_returned = nested("nested")
    return {
        "returned_self": returned is middleware,
        "init": middleware.storage.init,
        "marker": middleware.marker,
        "data": middleware.read(),
        "nested_returned_self": nested_returned is nested,
        "nested_types": [type(nested.storage).__name__, type(nested.storage.storage).__name__],
        "nested_init": nested.storage.storage.init,
    }


def middleware_caching() -> dict[str, Any]:
    caching = CachingMiddleware(RecordingStorage)
    caching()
    caching.WRITE_CACHE_SIZE = 3
    first_read = caching.read()
    second_read = caching.read()
    reads_after_two = caching.storage.reads
    caching.write({"v": 1})
    caching.write({"v": 2})
    before_threshold = len(caching.storage.writes)
    caching.write({"v": 3})
    after_threshold = len(caching.storage.writes)
    caching.write({"v": 4})
    caching.close()
    return {
        "reads": [first_read, second_read],
        "underlying_reads": reads_after_two,
        "before_threshold": before_threshold,
        "after_threshold": after_threshold,
        "writes": caching.storage.writes,
        "modified_count": caching._cache_modified_count,
        "close_count": caching.storage.close_count,
    }


def middleware_json() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="tinydb-middleware-") as temporary:
        path = Path(temporary) / "db.json"
        with TinyDB(str(path), storage=CachingMiddleware(JSONStorage), ensure_ascii=False) as db:
            db.insert({"name": "café"})
            before_close = path.read_text(encoding="utf-8")
        after_close = json.loads(path.read_text(encoding="utf-8"))
        handle_closed = db.storage.storage._handle.closed
        with TinyDB(str(path), storage=CachingMiddleware(JSONStorage), encoding="utf-8") as reopened:
            observed = docs(reopened.all())
        return {
            "before_close": before_close,
            "after_close": after_close,
            "handle_closed": handle_closed,
            "observed": observed,
        }


def query_cache() -> dict[str, Any]:
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{"v": 1}, {"v": 2}, {"v": 3}])

    class CountingQuery:
        def __init__(self, cacheable: bool):
            self.calls = 0
            self.cacheable = cacheable

        def __call__(self, value):
            self.calls += 1
            return value["v"] >= 2

        def __hash__(self):
            return 42 if self.cacheable else 43

        def is_cacheable(self):
            return self.cacheable

    condition = CountingQuery(True)
    first = db.search(condition)
    second = db.search(condition)
    same_document = first[0] is second[0]
    fresh_list = first is not second
    first[0]["mutated"] = True
    mutation_visible = db.search(condition)[0]["mutated"]
    calls_before_write = condition.calls
    db.insert({"v": 4})
    after_write = docs(db.search(condition))
    uncacheable = CountingQuery(False)
    db.search(uncacheable)
    db.search(uncacheable)
    return {
        "first": docs(first),
        "same_document": same_document,
        "fresh_list": fresh_list,
        "mutation_visible": mutation_visible,
        "calls_before_write": calls_before_write,
        "calls_after_write": condition.calls,
        "after_write": after_write,
        "uncacheable_calls": uncacheable.calls,
    }


def lru_eviction() -> dict[str, Any]:
    cache = LRUCache(capacity=3)
    cache["a"] = 0
    cache["b"] = 1
    cache["c"] = 2
    first_order = cache.lru
    cache.get("a")
    touched_order = cache.lru
    cache["d"] = 4
    evicted_order = cache.lru
    cache.set("a", 5)
    updated_order = cache.lru
    return {
        "orders": [first_order, touched_order, evicted_order, updated_order],
        "values": [cache["c"], cache["d"], cache["a"]],
        "contains_b": "b" in cache,
        "length": cache.length,
    }


def lru_mapping() -> dict[str, Any]:
    cache = LRUCache()
    cache["zero"] = 0
    cache["false"] = False
    cache["none"] = None
    missing = error_details(cache.__getitem__, "missing")
    none_value = error_details(cache.__getitem__, "none")
    default = cache.get("missing", "fallback")
    del cache["false"]
    keys = list(cache)
    cache.clear()
    return {
        "missing": missing,
        "none_value": none_value,
        "default": default,
        "keys_before_clear": keys,
        "length_after_clear": len(cache),
        "capacity": cache.capacity,
    }


def freeze_values() -> dict[str, Any]:
    frozen = freeze([1, {"b": [2, {"a": 3}]}, {4, 5}, (6, {"c": 7})])
    mapping = frozen[1]
    return {
        "types": [type(frozen).__name__, type(mapping).__name__, type(mapping["b"]).__name__, type(frozen[2]).__name__, type(frozen[3]).__name__, type(frozen[3][1]).__name__],
        "values": [frozen[0], mapping, sorted(frozen[2]), frozen[3]],
        "hashable": isinstance(hash(mapping), int),
        "set_error": error_details(mapping.__setitem__, "x", 1),
        "pop_error": error_details(mapping.pop, "b"),
        "update_error": error_details(mapping.update, {"x": 1}),
    }


def document_behavior() -> dict[str, Any]:
    original = {"name": "Ada", "nested": {"v": 1}}
    document = Document(original, 7)
    document["name"] = "Grace"
    return {
        "dict": dict(document),
        "doc_id": document.doc_id,
        "is_dict": isinstance(document, dict),
        "original": original,
        "equality": document == {"name": "Grace", "nested": {"v": 1}},
    }


OPERATIONS = {
    function.__name__: function
    for function in (
        package_surface,
        storage_memory,
        storage_json,
        storage_json_modes,
        storage_contract,
        query_comparisons,
        query_logic,
        query_paths,
        query_regex,
        query_collections,
        query_fragment,
        query_custom_cacheability,
        query_errors,
        table_insert,
        table_insert_multiple,
        table_get,
        table_search,
        table_update_mapping,
        table_update_operations,
        table_update_multiple,
        table_remove,
        table_upsert,
        table_truncate_persist,
        table_errors,
        database_tables,
        database_default,
        database_json_persistence,
        database_context,
        middleware_forwarding,
        middleware_caching,
        middleware_json,
        query_cache,
        lru_eviction,
        lru_mapping,
        freeze_values,
        document_behavior,
    )
}


def main() -> None:
    for line in sys.stdin:
        request: Any = None
        try:
            request = json.loads(line)
            request_id = request["id"]
            operation = request["operation"]
            result = OPERATIONS[operation]()
            response = {"id": request_id, "ok": True, "result": result}
        except Exception as exc:
            response = {
                "id": request.get("id") if isinstance(request, dict) else None,
                "ok": False,
                "error": {"type": type(exc).__name__, "message": str(exc)},
            }
        print(json.dumps(response, ensure_ascii=True, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
