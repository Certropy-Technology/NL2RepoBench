#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import re
import sys
import tempfile
from pathlib import Path


def _load_candidate(candidate: Path):
    dependencies = Path("/opt/candidate-dependencies/site")
    if dependencies.is_dir():
        sys.path.insert(0, str(dependencies))
    sys.path.insert(0, str(candidate))
    spec = importlib.util.find_spec("alembic")
    if spec is None or not spec.origin:
        raise ModuleNotFoundError("alembic is not installed by the candidate")
    origin = Path(spec.origin).resolve()
    if not origin.is_relative_to(candidate.resolve()):
        raise ModuleNotFoundError("alembic was not loaded from candidate-owned site")
    import alembic
    import sqlalchemy as sa
    from alembic import command
    from alembic.config import Config
    from alembic.operations import Operations, ops
    from alembic.runtime.migration import MigrationContext
    from alembic.script import ScriptDirectory

    return alembic, sa, command, Config, Operations, ops, MigrationContext, ScriptDirectory


def _offline_sql(MigrationContext, Operations, url: str, action) -> str:
    output = io.StringIO()
    context = MigrationContext.configure(url=url, opts={"as_sql": True, "output_buffer": output})
    action(Operations(context))
    return output.getvalue().strip()


def run(request: dict[str, object], candidate: Path) -> dict[str, object]:
    (
        alembic,
        sa,
        command,
        Config,
        Operations,
        ops,
        MigrationContext,
        ScriptDirectory,
    ) = _load_candidate(candidate)
    operation = request.get("operation")

    if operation == "metadata":
        return {
            "version_is_string": isinstance(getattr(alembic, "__version__", None), str),
            "config": isinstance(Config(), Config),
            "command_callables": all(callable(getattr(command, name, None)) for name in ("init", "revision", "upgrade", "downgrade", "stamp", "current")),
            "operation_classes": all(isinstance(getattr(ops, name, None), type) for name in ("CreateTableOp", "AddColumnOp", "CreateIndexOp", "AlterColumnOp")),
        }
    if operation == "config_defaults":
        config = Config()
        return {"section": config.config_ini_section, "url": config.get_main_option("sqlalchemy.url")}
    if operation == "config_set_options":
        config = Config()
        config.set_main_option("script_location", "pkg:migrations")
        config.set_section_option("custom", "answer", "42")
        config.attributes["connection"] = "sentinel"
        return {
            "script_location": config.get_main_option("script_location"),
            "section_value": config.get_section_option("custom", "answer"),
            "attributes": config.attributes["connection"],
        }
    if operation == "config_file":
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "alembic.ini"
            path.write_text("[alembic]\nscript_location = migrations\nsqlalchemy.url = sqlite:///demo.db\n[custom]\nanswer = 42\n", encoding="utf-8")
            config = Config(str(path))
            return {
                "name": Path(config.config_file_name).name if config.config_file_name else None,
                "location": config.get_main_option("script_location"),
                "url": config.get_main_option("sqlalchemy.url"),
                "custom": config.get_section_option("custom", "answer"),
            }
    if operation == "config_output":
        output = io.StringIO()
        config = Config(stdout=output)
        config.print_stdout("migration %s", "ready")
        return {"output": output.getvalue()}
    if operation == "context_dialects":
        sqlite = MigrationContext.configure(url="sqlite://")
        postgres = MigrationContext.configure(dialect_name="postgresql")
        return {"sqlite": sqlite.dialect.name, "postgres": postgres.dialect.name, "as_sql": sqlite.as_sql}
    if operation == "offline_sqlite_table":
        return {"sql": _offline_sql(MigrationContext, Operations, "sqlite://", lambda op: op.create_table("account", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(50), nullable=False)))}
    if operation == "offline_postgres_column":
        return {"sql": _offline_sql(MigrationContext, Operations, "postgresql://", lambda op: op.add_column("account", sa.Column("email", sa.String(255))))}
    if operation == "offline_sqlite_index":
        return {"sql": _offline_sql(MigrationContext, Operations, "sqlite://", lambda op: op.create_index("ix_account_email", "account", ["email"], unique=True))}
    if operation == "offline_postgres_drop":
        return {"sql": _offline_sql(MigrationContext, Operations, "postgresql://", lambda op: op.drop_table("account"))}
    if operation == "offline_sqlite_execute":
        return {"sql": _offline_sql(MigrationContext, Operations, "sqlite://", lambda op: op.execute("UPDATE account SET name = 'ready'"))}
    if operation == "create_index_op":
        op = ops.CreateIndexOp("ix_account_email", "account", ["email"], unique=True, schema="audit")
        return {"name": op.index_name, "table": op.table_name, "columns": op.columns, "unique": op.unique, "schema": op.schema, "reverse": type(op.reverse()).__name__}
    if operation == "add_column_op":
        op = ops.AddColumnOp("account", sa.Column("email", sa.String(120), nullable=False), schema="audit")
        return {"table": op.table_name, "name": op.column.name, "type": str(op.column.type), "nullable": op.column.nullable, "schema": op.schema, "reverse": type(op.reverse()).__name__}
    if operation == "alter_column_op":
        op = ops.AlterColumnOp("account", "name", existing_type=sa.String(50), modify_nullable=False, modify_type=sa.Text())
        return {"table": op.table_name, "column": op.column_name, "existing": str(op.existing_type), "modify": str(op.modify_type), "nullable": op.modify_nullable}
    if operation == "create_table_op":
        table = sa.Table("account", sa.MetaData(), sa.Column("id", sa.Integer(), primary_key=True), sa.Column("email", sa.String(80), nullable=False))
        op = ops.CreateTableOp.from_table(table)
        return {"table": op.table_name, "columns": [column.name for column in op.columns if isinstance(column, sa.Column)], "reverse": type(op.reverse()).__name__}
    if operation == "upgrade_ops":
        upgrade = ops.UpgradeOps(ops=[ops.AddColumnOp("account", sa.Column("name", sa.String(30)))])
        return {"is_empty": upgrade.is_empty(), "diff_count": len(upgrade.as_diffs()), "reverse": type(upgrade.reverse()).__name__}
    if operation == "command_init":
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "migrations"
            config = Config(str(Path(directory) / "alembic.ini"), stdout=io.StringIO())
            with contextlib.redirect_stdout(io.StringIO()):
                command.init(config, str(root), template="generic")
            return {"files": sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()), "versions": (root / "versions").is_dir()}
    if operation == "command_revision":
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "migrations"
            config = Config(str(Path(directory) / "alembic.ini"), stdout=io.StringIO())
            with contextlib.redirect_stdout(io.StringIO()):
                command.init(config, str(root), template="generic")
            config.set_main_option("script_location", str(root))
            with contextlib.redirect_stdout(io.StringIO()):
                revision = command.revision(config, message="create account", rev_id="a1b2c3d4e5f6")
            return {"revision": revision.revision, "down_revision": revision.down_revision, "path_name": Path(revision.path).name, "exists": Path(revision.path).is_file()}
    if operation == "script_directory":
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "migrations"
            config = Config(str(Path(directory) / "alembic.ini"), stdout=io.StringIO())
            with contextlib.redirect_stdout(io.StringIO()):
                command.init(config, str(root), template="generic")
            config.set_main_option("script_location", str(root))
            script = ScriptDirectory.from_config(config)
            return {"dir_name": Path(script.dir).name, "version_locations": [Path(item).name for item in script.version_locations], "has_revision_map": script.revision_map is not None}
    if operation == "revision_id":
        from alembic.util import rev_id
        value = rev_id()
        return {"value": value, "matches": bool(re.fullmatch(r"[0-9a-f]{12}", value))}
    raise ValueError(f"unsupported operation: {operation!r}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    args = parser.parse_args()
    for line in sys.stdin:
        try:
            request = json.loads(line)
            if not isinstance(request, dict):
                raise TypeError("request must be an object")
            response = run(request, args.candidate)
        except Exception as exc:
            response = {"error": {"type": type(exc).__name__, "message": str(exc)[:512]}}
        print(json.dumps(response, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
