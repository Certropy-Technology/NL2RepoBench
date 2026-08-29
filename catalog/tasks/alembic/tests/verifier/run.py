from __future__ import annotations

import json
import os
import select
import signal
import shutil
import subprocess
from pathlib import Path


ROOT = Path("/tests/verifier")
CASES = [
    ("metadata", {"version_is_string": True, "config": True, "command_callables": True, "operation_classes": True}),
    ("config_defaults", {"section": "alembic", "url": None}),
    ("config_set_options", {"script_location": "pkg:migrations", "section_value": "42", "attributes": "sentinel"}),
    ("config_file", {"name": "alembic.ini", "location": "migrations", "url": "sqlite:///demo.db", "custom": "42"}),
    ("config_output", {"output": "migration ready\n"}),
    ("context_dialects", {"sqlite": "sqlite", "postgres": "postgresql", "as_sql": False}),
    ("offline_sqlite_table", {"sql": "CREATE TABLE account (\n    id INTEGER NOT NULL, \n    name VARCHAR(50) NOT NULL, \n    PRIMARY KEY (id)\n);"}),
    ("offline_postgres_column", {"sql": "ALTER TABLE account ADD COLUMN email VARCHAR(255);"}),
    ("offline_sqlite_index", {"sql": "CREATE UNIQUE INDEX ix_account_email ON account (email);"}),
    ("offline_postgres_drop", {"sql": "DROP TABLE account;"}),
    ("offline_sqlite_execute", {"sql": "UPDATE account SET name = 'ready';"}),
    ("create_index_op", {"name": "ix_account_email", "table": "account", "columns": ["email"], "unique": True, "schema": "audit", "reverse": "DropIndexOp"}),
    ("add_column_op", {"table": "account", "name": "email", "type": "VARCHAR(120)", "nullable": False, "schema": "audit", "reverse": "DropColumnOp"}),
    ("alter_column_op", {"table": "account", "column": "name", "existing": "VARCHAR(50)", "modify": "TEXT", "nullable": False}),
    ("create_table_op", {"table": "account", "columns": ["id", "email"], "reverse": "DropTableOp"}),
    ("upgrade_ops", {"is_empty": False, "diff_count": 1, "reverse": "DowngradeOps"}),
    ("command_init", {"files": ["README", "env.py", "script.py.mako"], "versions": True}),
    ("command_revision", {"revision": "a1b2c3d4e5f6", "down_revision": None, "path_name": "a1b2c3d4e5f6_create_account.py", "exists": True}),
    ("script_directory", {"dir_name": "migrations", "version_locations": [], "has_revision_map": True}),
    ("revision_id", {"matches": True}),
]


def main() -> None:
    adapter = Path("/tmp/alembic-candidate-rpc.py")
    shutil.copyfile(ROOT / "candidate_rpc.py", adapter)
    adapter.chmod(0o555)
    process = subprocess.Popen(
        ["runuser", "-u", "candidate", "--", "env", "HOME=/tmp/candidate-build/home", "TMPDIR=/tmp/candidate-build/tmp", "/usr/local/bin/python", "-I", str(adapter), "--candidate", "/tmp/candidate-site"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        start_new_session=True,
    )
    leaves: list[dict[str, object]] = []
    unavailable = False
    try:
        assert process.stdin and process.stdout
        for operation, expected in CASES:
            if unavailable:
                leaves.append({"id": operation, "status": "failed", "message": "candidate unavailable"})
                continue
            process.stdin.write(json.dumps({"operation": operation}) + "\n")
            process.stdin.flush()
            ready, _, _ = select.select([process.stdout], [], [], 15.0)
            if not ready:
                leaves.append({"id": operation, "status": "failed", "message": "candidate timeout"})
                unavailable = True
                os.killpg(process.pid, signal.SIGTERM)
                continue
            line = process.stdout.readline()
            if not line:
                leaves.append({"id": operation, "status": "failed", "message": "candidate exited"})
                unavailable = True
                continue
            response = json.loads(line)
            passed = "error" not in response and all(response.get(key) == value for key, value in expected.items())
            leaves.append({"id": operation, "status": "passed" if passed else "failed", "message": "" if passed else json.dumps(response, sort_keys=True)[:512]})
    finally:
        if process.stdin:
            process.stdin.close()
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
        process.wait(timeout=10)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
