"""Private deterministic scenarios for the records public contract.

Each scenario runs as the unprivileged candidate in an isolated subprocess and
must be derivable from the public instruction (https://github.com/kennethreitz/records,
v0.6.0, immutable revision 72efce67874d1b40ac2a35542127e8830da49707). The
candidate runner executes the script and reads the ``result`` binding.
"""

from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


def _run(source: str, expected: object) -> tuple[str, object]:
    observed = execute_script(source, timeout_sec=20.0)
    actual: dict[str, object] = {"ok": observed.ok, "value": observed.value}
    if not observed.ok:
        actual["exception_type"] = observed.exception_type
        actual["exception_message"] = observed.exception_message
    return "passed" if actual == expected else "failed", actual


CASES: list[tuple[str, str, object]] = [
    ("import-surface", """import records
result = [hasattr(records, 'Database'), hasattr(records, 'Record'), hasattr(records, 'RecordCollection')]""", {"ok": True, "value": [True, True, True]}),
    ("database-connect-memory", """import records
db = records.Database('sqlite:///:memory:')
result = db is not None""", {"ok": True, "value": True}),
    ("database-simple-query", """import records
db = records.Database('sqlite:///:memory:')
rows = db.query('SELECT 1 as id, "test" as name')
result = [rows.first().id, rows.first().name]""", {"ok": True, "value": [1, "test"]}),
    ("record-dict-access", """import records
db = records.Database('sqlite:///:memory:')
row = db.query('SELECT 1 as id, "Alice" as name').first()
result = [row['id'], row['name']]""", {"ok": True, "value": [1, "Alice"]}),
    ("record-attr-access", """import records
db = records.Database('sqlite:///:memory:')
row = db.query('SELECT 1 as id, "Bob" as name').first()
result = [row.id, row.name]""", {"ok": True, "value": [1, "Bob"]}),
    ("record-index-access", """import records
db = records.Database('sqlite:///:memory:')
row = db.query('SELECT 1 as id, "Charlie" as name').first()
result = [row[0], row[1]]""", {"ok": True, "value": [1, "Charlie"]}),
    ("record-as-dict", """import records
db = records.Database('sqlite:///:memory:')
row = db.query('SELECT 1 as id, "Dave" as name').first()
d = row.as_dict()
result = [d['id'], d['name'], type(d).__name__]""", {"ok": True, "value": [1, "Dave", "dict"]}),
    ("record-as-dict-ordered", """import records
from collections import OrderedDict
db = records.Database('sqlite:///:memory:')
row = db.query('SELECT 1 as id, "Eve" as name').first()
d = row.as_dict(ordered=True)
result = [isinstance(d, OrderedDict), d['id'], d['name']]""", {"ok": True, "value": [True, 1, "Eve"]}),
    ("record-keys-values", """import records
db = records.Database('sqlite:///:memory:')
row = db.query('SELECT 1 as id, "Frank" as name').first()
result = [list(row.keys()), list(row.values())]""", {"ok": True, "value": [["id", "name"], [1, "Frank"]]}),
    ("record-get", """import records
db = records.Database('sqlite:///:memory:')
row = db.query('SELECT 1 as id').first()
result = [row.get('id'), row.get('missing', 'default')]""", {"ok": True, "value": [1, "default"]}),
    ("record-items", """import records
db = records.Database('sqlite:///:memory:')
row = db.query('SELECT 1 as id, 2 as val').first()
items = list(row.as_dict().items())
result = [len(items), items[0][0], items[1][1]]""", {"ok": True, "value": [2, "id", 2]}),
    ("recordcollection-all", """import records
db = records.Database('sqlite:///:memory:')
db.query('CREATE TABLE t (id INTEGER)')
db.query('INSERT INTO t VALUES (1), (2), (3)')
rows = db.query('SELECT * FROM t ORDER BY id')
all_rows = rows.all()
result = [len(all_rows), all_rows[0].id, all_rows[2].id]""", {"ok": True, "value": [3, 1, 3]}),
    ("recordcollection-first", """import records
db = records.Database('sqlite:///:memory:')
db.query('CREATE TABLE t (id INTEGER)')
db.query('INSERT INTO t VALUES (10), (20)')
rows = db.query('SELECT * FROM t ORDER BY id')
result = rows.first().id""", {"ok": True, "value": 10}),
    ("recordcollection-first-default", """import records
db = records.Database('sqlite:///:memory:')
rows = db.query('SELECT 1 as id WHERE 0=1')
result = rows.first(default='empty')""", {"ok": True, "value": "empty"}),
    ("recordcollection-first-as-dict", """import records
db = records.Database('sqlite:///:memory:')
db.query('CREATE TABLE t (id INTEGER)')
db.query('INSERT INTO t VALUES (42)')
rows = db.query('SELECT * FROM t')
result = rows.first(as_dict=True)""", {"ok": True, "value": {"id": 42}}),
    ("recordcollection-one", """import records
db = records.Database('sqlite:///:memory:')
db.query('CREATE TABLE t (id INTEGER)')
db.query('INSERT INTO t VALUES (99)')
rows = db.query('SELECT * FROM t')
result = rows.one().id""", {"ok": True, "value": 99}),
    ("recordcollection-scalar", """import records
db = records.Database('sqlite:///:memory:')
rows = db.query('SELECT 42 as answer')
result = rows.scalar()""", {"ok": True, "value": 42}),
    ("recordcollection-scalar-default", """import records
db = records.Database('sqlite:///:memory:')
rows = db.query('SELECT 1 WHERE 0=1')
result = rows.scalar(default=-1)""", {"ok": True, "value": -1}),
    ("recordcollection-all-as-dict", """import records
db = records.Database('sqlite:///:memory:')
db.query('CREATE TABLE t (id INTEGER)')
db.query('INSERT INTO t VALUES (1), (2)')
rows = db.query('SELECT * FROM t ORDER BY id')
all_dicts = rows.all(as_dict=True)
result = [len(all_dicts), all_dicts[0]['id'], all_dicts[1]['id']]""", {"ok": True, "value": [2, 1, 2]}),
    ("recordcollection-as-dict", """import records
db = records.Database('sqlite:///:memory:')
db.query('CREATE TABLE t (id INTEGER, name TEXT)')
db.query('INSERT INTO t VALUES (1, "A"), (2, "B")')
rows = db.query('SELECT * FROM t ORDER BY id')
dicts = rows.as_dict()
result = [len(dicts), dicts[0]['name'], dicts[1]['name']]""", {"ok": True, "value": [2, "A", "B"]}),
    ("recordcollection-iteration", """import records
db = records.Database('sqlite:///:memory:')
db.query('CREATE TABLE t (id INTEGER)')
db.query('INSERT INTO t VALUES (1), (2), (3)')
rows = db.query('SELECT * FROM t ORDER BY id')
ids = [row.id for row in rows]
result = ids""", {"ok": True, "value": [1, 2, 3]}),
    ("recordcollection-len", """import records
db = records.Database('sqlite:///:memory:')
db.query('CREATE TABLE t (id INTEGER)')
db.query('INSERT INTO t VALUES (1), (2), (3), (4), (5)')
rows = db.query('SELECT * FROM t')
result = len(rows.all())""", {"ok": True, "value": 5}),
    ("database-query-params", """import records
db = records.Database('sqlite:///:memory:')
db.query('CREATE TABLE users (id INTEGER, name TEXT)')
db.query('INSERT INTO users VALUES (1, "Alice"), (2, "Bob")')
rows = db.query('SELECT * FROM users WHERE id = :uid', uid=1)
result = rows.first().name""", {"ok": True, "value": "Alice"}),
    ("database-get-table-names", """import records
db = records.Database('sqlite:///:memory:')
db.query('CREATE TABLE foo (id INTEGER)')
db.query('CREATE TABLE bar (id INTEGER)')
tables = db.get_table_names()
result = [len(tables), 'foo' in tables, 'bar' in tables]""", {"ok": True, "value": [2, True, True]}),
    ("database-transaction-commit", """import records
db = records.Database('sqlite:///:memory:')
db.query('CREATE TABLE t (id INTEGER)')
with db.transaction() as conn:
    conn.query('INSERT INTO t VALUES (1)')
result = db.query('SELECT COUNT(*) as cnt FROM t').scalar()""", {"ok": True, "value": 1}),
    ("database-transaction-rollback", """import records
db = records.Database('sqlite:///:memory:')
db.query('CREATE TABLE t (id INTEGER)')
try:
    with db.transaction() as conn:
        conn.query('INSERT INTO t VALUES (1)')
        raise ValueError('test')
except ValueError:
    pass
result = db.query('SELECT COUNT(*) as cnt FROM t').scalar()""", {"ok": True, "value": 0}),
    ("database-close", """import records
db = records.Database('sqlite:///:memory:')
db.query('SELECT 1')
db.close()
result = True""", {"ok": True, "value": True}),
    ("multiple-queries", """import records
db = records.Database('sqlite:///:memory:')
db.query('CREATE TABLE t (id INTEGER)')
db.query('INSERT INTO t VALUES (1)')
db.query('INSERT INTO t VALUES (2)')
cnt = db.query('SELECT COUNT(*) as cnt FROM t').scalar()
result = cnt""", {"ok": True, "value": 2}),
    ("record-export-csv", """import records
db = records.Database('sqlite:///:memory:')
row = db.query('SELECT 1 as id, "test" as name').first()
csv = row.export('csv')
result = ['id' in csv, 'name' in csv, 'test' in csv]""", {"ok": True, "value": [True, True, True]}),
    ("recordcollection-export-csv", """import records
db = records.Database('sqlite:///:memory:')
db.query('CREATE TABLE t (id INTEGER)')
db.query('INSERT INTO t VALUES (1), (2)')
rows = db.query('SELECT * FROM t ORDER BY id')
csv = rows.export('csv')
result = 'id' in csv""", {"ok": True, "value": True}),
    ("recordcollection-export-json", """import records
db = records.Database('sqlite:///:memory:')
db.query('CREATE TABLE t (id INTEGER)')
db.query('INSERT INTO t VALUES (10)')
rows = db.query('SELECT * FROM t')
json_str = rows.export('json')
result = '10' in json_str""", {"ok": True, "value": True}),
    ("record-multiple-columns", """import records
db = records.Database('sqlite:///:memory:')
row = db.query('SELECT 1 as a, 2 as b, 3 as c, 4 as d').first()
result = [row.a, row.b, row.c, row.d]""", {"ok": True, "value": [1, 2, 3, 4]}),
    ("record-null-value", """import records
db = records.Database('sqlite:///:memory:')
row = db.query('SELECT NULL as val').first()
result = row.val is None""", {"ok": True, "value": True}),
    ("recordcollection-empty", """import records
db = records.Database('sqlite:///:memory:')
rows = db.query('SELECT 1 WHERE 0=1')
result = len(rows.all())""", {"ok": True, "value": 0}),
    ("database-table-operations", """import records
db = records.Database('sqlite:///:memory:')
db.query('CREATE TABLE test1 (id INTEGER)')
db.query('CREATE TABLE test2 (val TEXT)')
db.query('DROP TABLE test1')
tables = db.get_table_names()
result = ['test1' not in tables, 'test2' in tables]""", {"ok": True, "value": [True, True]}),
    ("query-with-where", """import records
db = records.Database('sqlite:///:memory:')
db.query('CREATE TABLE t (id INTEGER, active INTEGER)')
db.query('INSERT INTO t VALUES (1, 1), (2, 0), (3, 1)')
rows = db.query('SELECT * FROM t WHERE active = 1 ORDER BY id')
ids = [r.id for r in rows]
result = ids""", {"ok": True, "value": [1, 3]}),
    ("query-with-join", """import records
db = records.Database('sqlite:///:memory:')
db.query('CREATE TABLE users (id INTEGER, name TEXT)')
db.query('CREATE TABLE orders (id INTEGER, user_id INTEGER)')
db.query('INSERT INTO users VALUES (1, "Alice")')
db.query('INSERT INTO orders VALUES (10, 1)')
row = db.query('SELECT u.name, o.id as order_id FROM users u JOIN orders o ON u.id = o.user_id').first()
result = [row.name, row.order_id]""", {"ok": True, "value": ["Alice", 10]}),
    ("query-aggregate", """import records
db = records.Database('sqlite:///:memory:')
db.query('CREATE TABLE t (val INTEGER)')
db.query('INSERT INTO t VALUES (10), (20), (30)')
row = db.query('SELECT SUM(val) as total, COUNT(*) as cnt, AVG(val) as avg FROM t').first()
result = [row.total, row.cnt, int(row.avg)]""", {"ok": True, "value": [60, 3, 20]}),
    ("query-order-by", """import records
db = records.Database('sqlite:///:memory:')
db.query('CREATE TABLE t (id INTEGER)')
db.query('INSERT INTO t VALUES (3), (1), (2)')
rows = db.query('SELECT * FROM t ORDER BY id ASC')
ids = [r.id for r in rows]
result = ids""", {"ok": True, "value": [1, 2, 3]}),
    ("query-limit", """import records
db = records.Database('sqlite:///:memory:')
db.query('CREATE TABLE t (id INTEGER)')
db.query('INSERT INTO t VALUES (1), (2), (3), (4), (5)')
rows = db.query('SELECT * FROM t LIMIT 2')
result = len(rows.all())""", {"ok": True, "value": 2}),
    ("transaction-multiple-inserts", """import records
db = records.Database('sqlite:///:memory:')
db.query('CREATE TABLE t (id INTEGER)')
with db.transaction() as conn:
    conn.query('INSERT INTO t VALUES (1)')
    conn.query('INSERT INTO t VALUES (2)')
    conn.query('INSERT INTO t VALUES (3)')
result = db.query('SELECT COUNT(*) as cnt FROM t').scalar()""", {"ok": True, "value": 3}),
    ("connection-query", """import records
db = records.Database('sqlite:///:memory:')
db.query('CREATE TABLE t (id INTEGER)')
db.query('INSERT INTO t VALUES (42)')
conn = db.get_connection()
row = conn.query('SELECT * FROM t').first()
conn.close()
result = row.id""", {"ok": True, "value": 42}),
    ("record-dataset-access", """import records
db = records.Database('sqlite:///:memory:')
row = db.query('SELECT 1 as id, "test" as name').first()
ds = row.dataset
result = [len(ds), ds.headers[0], ds.headers[1]]""", {"ok": True, "value": [1, "id", "name"]}),
    ("recordcollection-dataset", """import records
db = records.Database('sqlite:///:memory:')
db.query('CREATE TABLE t (id INTEGER)')
db.query('INSERT INTO t VALUES (1), (2)')
rows = db.query('SELECT * FROM t ORDER BY id')
ds = rows.dataset
result = [len(ds), len(ds.headers)]""", {"ok": True, "value": [2, 1]}),
    ("query-text-values", """import records
db = records.Database('sqlite:///:memory:')
db.query('CREATE TABLE t (name TEXT)')
db.query('INSERT INTO t VALUES ("Alice"), ("Bob"), ("Charlie")')
rows = db.query('SELECT * FROM t ORDER BY name')
names = [r.name for r in rows]
result = names""", {"ok": True, "value": ["Alice", "Bob", "Charlie"]}),
    ("query-mixed-types", """import records
db = records.Database('sqlite:///:memory:')
db.query('CREATE TABLE t (id INTEGER, name TEXT, score REAL)')
db.query('INSERT INTO t VALUES (1, "Alice", 95.5)')
row = db.query('SELECT * FROM t').first()
result = [row.id, row.name, row.score]""", {"ok": True, "value": [1, "Alice", 95.5]}),
    ("record-get-multiple", """import records
db = records.Database('sqlite:///:memory:')
row = db.query('SELECT 1 as a, 2 as b').first()
result = [row.get('a'), row.get('b'), row.get('c', 99)]""", {"ok": True, "value": [1, 2, 99]}),
    ("recordcollection-one-default", """import records
db = records.Database('sqlite:///:memory:')
rows = db.query('SELECT 1 WHERE 0=1')
result = rows.one(default='none')""", {"ok": True, "value": "none"}),
]


def main() -> None:
    leaves: list[dict[str, object]] = []
    for case_id, source, expected in CASES:
        status, actual = _run(source, expected)
        leaf: dict[str, object] = {"id": case_id, "status": status}
        if status == "failed":
            leaf["message"] = json.dumps(actual, ensure_ascii=False, sort_keys=True)
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
