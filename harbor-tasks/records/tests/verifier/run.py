"""Trusted custom-json-v1 verifier for the frozen `records` slice.

This module is root/trusted. It must never import candidate code. Every
behavioural probe runs in an unprivileged child process (`runuser -u candidate`,
`python -I`) that speaks a one-shot JSON request/response contract over pipes.

The 31 leaves mirror the frozen upstream collection at revision
72efce67874d1b40ac2a35542127e8830da49707 one-for-one:

  * 21 leaves for `tests/test_records.py::TestRecordCollection`
  * 2 leaves for `tests/test_records.py::TestRecord`
  * 1 leaf for `tests/test_105.py::test_issue105[sqlite_memory]`
  * 1 leaf for `tests/test_69.py::test_issue69[sqlite_memory]`
  * 6 leaves for `tests/test_transactions.py` (the `sqlite_memory` fixture param)

Every database probe uses `sqlite:///:memory:` only, so the slice stays offline
and needs no external database service.
"""

from __future__ import annotations

import json
import subprocess
import sys

# The child is deliberately a single source string: `python -I` ignores
# PYTHONPATH, so the candidate site and the locked dependency site are both
# inserted explicitly.
CHILD = r'''
import json, os, sys

sys.path.insert(0, os.environ["NL2REPO_CANDIDATE_DEPENDENCIES"])
sys.path.insert(0, os.environ["CANDIDATE_ROOT"])

from collections import namedtuple

import records

IdRecord = namedtuple("IdRecord", "id")


class Cheese(Exception):
    pass


def ids(rows):
    return [row.id for row in rows]


def collection(count):
    return records.RecordCollection(IdRecord(i) for i in range(count))


def empty():
    return records.RecordCollection(iter([]))


def memory_db():
    return records.Database("sqlite:///:memory:")


def with_foo_table(body):
    """Mirror the upstream `db` + `foo_table` fixture pair, including teardown."""

    db = memory_db()
    try:
        db.query("CREATE TABLE foo (a integer)")
        try:
            return body(db)
        finally:
            db.query("DROP TABLE foo")
    finally:
        db.close()


def foo_count(db):
    return db.query("SELECT count(*) AS n FROM foo")[0].n


def op_collection_iter():
    rows = collection(10)
    return [row.id for i, row in enumerate(rows) if row.id == i]


def op_collection_next():
    rows = collection(10)
    return [next(rows).id for _ in range(10)]


def op_collection_iter_and_next():
    rows = collection(10)
    i = enumerate(iter(rows))
    first_index, first_row = next(i)  # Cache first row.
    next(rows)  # Cache second row.
    second_index, second_row = next(i)  # Read second row from cache.
    return [first_index, first_row.id, second_index, second_row.id]


def op_collection_multiple_iter():
    rows = collection(10)
    i = enumerate(iter(rows))
    j = enumerate(iter(rows))
    seen = []
    for index, row in (next(i), next(j), next(j), next(i)):
        seen.extend([index, row.id])
    return seen


def op_collection_slice_iter():
    rows = collection(10)
    return {
        "sliced": ids(rows[:5]),
        "full": ids(rows),
        "len": len(rows),
    }


def op_collection_all():
    rows = collection(3)
    result = rows.all()
    return {"is_list": isinstance(result, list), "ids": [row.id for row in result]}


def op_collection_first():
    return collection(1).first().id


def op_collection_first_default_none():
    return empty().first() is None


def op_collection_first_default_override():
    return empty().first("Cheese")


def op_collection_first_raises_class():
    return empty().first(Cheese)


def op_collection_first_raises_instance():
    return empty().first(Cheese("cheddar"))


def op_collection_one():
    return collection(1).one().id


def op_collection_one_default_none():
    return empty().one() is None


def op_collection_one_default_override():
    return empty().one("Cheese")


def op_collection_one_raises_when_more_than_one():
    return collection(3).one()


def op_collection_one_raises_class():
    return empty().one(Cheese)


def op_collection_one_raises_instance():
    return empty().one(Cheese("cheddar"))


def op_collection_scalar():
    return collection(1).scalar()


def op_collection_scalar_default_none():
    return empty().scalar() is None


def op_collection_scalar_default_override():
    return empty().scalar("Kaffe")


def op_collection_scalar_raises_when_more_than_one():
    return collection(3).scalar()


def op_record_dir():
    keys, values = ["id", "name", "email"], [1, "", ""]
    listing = dir(records.Record(keys, values))
    return all(key in listing for key in keys) and all(
        key in listing for key in dir(object)
    )


def op_record_duplicate_column():
    record = records.Record(["id", "name", "email", "email"], [1, "", "", ""])
    return record["email"]


def op_issue105():
    return with_foo_table(
        lambda db: db.query("select count(*) as n from foo").scalar()
    )


def op_issue69():
    db = memory_db()
    try:
        db.query("CREATE table users (id text)")
        db.query("SELECT * FROM users WHERE id = :user", user="Te'ArnaLambert")
        return True
    finally:
        db.close()


def op_transaction_plain_db():
    def body(db):
        db.query("INSERT INTO foo VALUES (42)")
        db.query("INSERT INTO foo VALUES (43)")
        return foo_count(db)

    return with_foo_table(body)


def op_transaction_plain_conn():
    def body(db):
        conn = db.get_connection()
        conn.query("INSERT INTO foo VALUES (42)")
        conn.query("INSERT INTO foo VALUES (43)")
        return conn.query("SELECT count(*) AS n FROM foo")[0].n

    return with_foo_table(body)


def op_transaction_failing_self_managed():
    def body(db):
        conn = db.get_connection()
        tx = conn.transaction()
        try:
            conn.query("INSERT INTO foo VALUES (42)")
            conn.query("INSERT INTO foo VALUES (43)")
            raise ValueError()
        except ValueError:
            tx.rollback()
        finally:
            conn.close()
        return foo_count(db)

    return with_foo_table(body)


def op_transaction_failing():
    def body(db):
        # The frozen v0.6.0 `Database.transaction` rolls back and suppresses the
        # raised exception, so control returns here without propagation.
        with db.transaction() as conn:
            conn.query("INSERT INTO foo VALUES (42)")
            conn.query("INSERT INTO foo VALUES (43)")
            raise ValueError()
        return foo_count(db)

    return with_foo_table(body)


def op_transaction_passing_self_managed():
    def body(db):
        conn = db.get_connection()
        tx = conn.transaction()
        conn.query("INSERT INTO foo VALUES (42)")
        conn.query("INSERT INTO foo VALUES (43)")
        tx.commit()
        conn.close()
        return foo_count(db)

    return with_foo_table(body)


def op_transaction_passing():
    def body(db):
        with db.transaction() as conn:
            conn.query("INSERT INTO foo VALUES (42)")
            conn.query("INSERT INTO foo VALUES (43)")
        return foo_count(db)

    return with_foo_table(body)


OPERATIONS = {
    name[len("op_"):]: value
    for name, value in sorted(globals().items())
    if name.startswith("op_")
}

try:
    request = json.load(sys.stdin)
    operation = OPERATIONS[request["op"]]
    print(
        json.dumps(
            {"ok": True, "value": operation()},
            allow_nan=False,
            ensure_ascii=False,
            sort_keys=True,
        )
    )
except Exception as exc:
    print(
        json.dumps(
            {
                "ok": False,
                "error": {"type": type(exc).__name__, "message": str(exc)},
            },
            sort_keys=True,
        )
    )
'''

# (leaf id, child operation, expected value, expected exception type)
CASES: tuple[tuple[str, str, object, str | None], ...] = (
    ("collection_iter", "collection_iter", list(range(10)), None),
    ("collection_next", "collection_next", list(range(10)), None),
    ("collection_iter_and_next", "collection_iter_and_next", [0, 0, 1, 1], None),
    (
        "collection_multiple_iter",
        "collection_multiple_iter",
        [0, 0, 0, 0, 1, 1, 1, 1],
        None,
    ),
    (
        "collection_slice_iter",
        "collection_slice_iter",
        {"sliced": list(range(5)), "full": list(range(10)), "len": 10},
        None,
    ),
    (
        "collection_all_returns_list_of_records",
        "collection_all",
        {"is_list": True, "ids": [0, 1, 2]},
        None,
    ),
    ("collection_first_returns_single_record", "collection_first", 0, None),
    ("collection_first_defaults_to_none", "collection_first_default_none", True, None),
    (
        "collection_first_default_is_overridable",
        "collection_first_default_override",
        "Cheese",
        None,
    ),
    (
        "collection_first_raises_exception_subclass",
        "collection_first_raises_class",
        None,
        "Cheese",
    ),
    (
        "collection_first_raises_exception_instance",
        "collection_first_raises_instance",
        None,
        "Cheese",
    ),
    ("collection_one_returns_single_record", "collection_one", 0, None),
    ("collection_one_defaults_to_none", "collection_one_default_none", True, None),
    (
        "collection_one_default_is_overridable",
        "collection_one_default_override",
        "Cheese",
        None,
    ),
    (
        "collection_one_raises_when_more_than_one",
        "collection_one_raises_when_more_than_one",
        None,
        "ValueError",
    ),
    (
        "collection_one_raises_exception_subclass",
        "collection_one_raises_class",
        None,
        "Cheese",
    ),
    (
        "collection_one_raises_exception_instance",
        "collection_one_raises_instance",
        None,
        "Cheese",
    ),
    ("collection_scalar_returns_single_value", "collection_scalar", 0, None),
    (
        "collection_scalar_defaults_to_none",
        "collection_scalar_default_none",
        True,
        None,
    ),
    (
        "collection_scalar_default_is_overridable",
        "collection_scalar_default_override",
        "Kaffe",
        None,
    ),
    (
        "collection_scalar_raises_when_more_than_one",
        "collection_scalar_raises_when_more_than_one",
        None,
        "ValueError",
    ),
    ("record_dir", "record_dir", True, None),
    ("record_duplicate_column", "record_duplicate_column", None, "KeyError"),
    ("issue105_scalar_on_empty_table", "issue105", 0, None),
    ("issue69_quoted_named_parameter", "issue69", True, None),
    ("transaction_plain_db", "transaction_plain_db", 2, None),
    ("transaction_plain_conn", "transaction_plain_conn", 2, None),
    (
        "transaction_failing_self_managed",
        "transaction_failing_self_managed",
        0,
        None,
    ),
    ("transaction_failing", "transaction_failing", 0, None),
    (
        "transaction_passing_self_managed",
        "transaction_passing_self_managed",
        2,
        None,
    ),
    ("transaction_passing", "transaction_passing", 2, None),
)

CHILD_COMMAND = (
    "runuser",
    "-u",
    "candidate",
    "--",
    "env",
    "CANDIDATE_ROOT=/tmp/candidate-site",
    "NL2REPO_CANDIDATE_DEPENDENCIES=/opt/candidate-dependencies/site",
    "HOME=/tmp/candidate-build/home",
    "TMPDIR=/tmp/candidate-build/tmp",
    "PYTHONDONTWRITEBYTECODE=1",
    "PYTHONHASHSEED=0",
    "LANG=C.UTF-8",
    "LC_ALL=C.UTF-8",
    "/usr/local/bin/python",
    "-I",
    "-c",
    CHILD,
)


def evaluate(operation: str, expected: object, error_type: str | None) -> bool:
    try:
        completed = subprocess.run(
            [*CHILD_COMMAND],
            input=json.dumps({"op": operation}),
            text=True,
            capture_output=True,
            timeout=20,
            check=False,
        )
        response = json.loads(completed.stdout.splitlines()[-1])
    except Exception:
        return False
    if error_type is not None:
        return (
            response.get("ok") is False
            and response.get("error", {}).get("type") == error_type
        )
    return response.get("ok") is True and response.get("value") == expected


def main() -> None:
    leaves = [
        {
            "id": leaf_id,
            "status": "passed" if evaluate(operation, expected, error_type) else "failed",
        }
        for leaf_id, operation, expected, error_type in CASES
    ]
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
