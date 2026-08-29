# Project Description

Build `alembic`, the database-migration toolkit for SQLAlchemy. Start with an empty workspace and provide a normal installable Python package. The task checks deterministic public configuration, migration-operation objects, offline SQL generation, and generic script-directory creation. It does not require a live database server or a network connection.

## Supports

- Python 3.10 or later and SQLAlchemy-compatible public APIs.
- `alembic`, `alembic.config`, `alembic.command`, `alembic.runtime.migration`, `alembic.operations`, and `alembic.script` imports.
- Programmatic `Config` objects and ordinary `.ini` configuration files.
- Offline migration SQL for SQLite and PostgreSQL, generated into a caller-provided text buffer.
- Local filesystem migration environments created with the built-in `generic` template.

## API Usage Guide

`alembic.config.Config(file_: str | os.PathLike | None = None, toml_file: str | os.PathLike | None = None, ini_section: str = "alembic", output_buffer: TextIO | None = None, stdout: TextIO = sys.stdout, cmd_opts: Namespace | None = None, config_args: Mapping[str, Any] = {}, attributes: dict[str, Any] | None = None)` represents Alembic configuration. `get_main_option(name, default=None)`, `set_main_option(name, value)`, `get_section_option(section, name, default=None)`, and `set_section_option(section, name, value)` read and mutate string options. `attributes` is a mutable dictionary for programmatic objects such as a connection. `print_stdout(text, *args)` writes a formatted line to its `stdout` stream.

`alembic.runtime.migration.MigrationContext.configure(connection=None, url=None, dialect_name=None, dialect=None, environment_context=None, dialect_opts=None, opts=None)` creates a migration context. With `opts={"as_sql": True, "output_buffer": stream}`, the context generates SQL without opening a database connection. A URL or `dialect_name` determines dialect-specific behavior.

`alembic.operations.Operations(context)` exposes migration directives including `create_table(table_name, *columns, **kw)`, `add_column(table_name, column, schema=None)`, `create_index(index_name, table_name, columns, unique=False, schema=None, **kw)`, `drop_table(table_name, schema=None, **kw)`, and `execute(sqltext, execution_options=None)`. In offline mode they append deterministic SQL to the configured output buffer.

Operation value classes live in `alembic.operations.ops`: `CreateTableOp.from_table(table)`, `AddColumnOp(table_name, column, schema=None, **kw)`, `CreateIndexOp(index_name, table_name, columns, unique=False, schema=None, **kw)`, `AlterColumnOp(table_name, column_name, **kw)`, and `UpgradeOps(ops=())`. Their public attributes describe the requested change; `reverse()` returns the corresponding reverse operation or operation container.

`alembic.command.init(config, directory, template="generic", package=False)` creates a local migration environment. `alembic.command.revision(config, message=None, autogenerate=False, sql=False, head="head", splice=False, branch_label=None, version_path=None, rev_id=None, depends_on=None, process_revision_directives=None)` creates a revision script. `alembic.script.ScriptDirectory.from_config(config)` resolves a configured script location and provides its revision map.

`alembic.util.rev_id()` returns a newly generated 12-character lowercase hexadecimal revision identifier. Its value is intentionally non-deterministic, but its shape is stable.

## Implementation Notes

Preserve public import paths, signatures, option handling, SQL dialect behavior, operation reversal, and filesystem layout of the generic template. SQL must be produced locally; no test scenario permits connecting to a database service. The private verifier sends one bounded JSON request at a time to an unprivileged candidate subprocess and checks only normalized public results. Do not add task-specific commands, test fixtures, or network behavior.
