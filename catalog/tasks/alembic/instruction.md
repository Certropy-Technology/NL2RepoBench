# Project Description

Build `alembic`, the database-migration toolkit for SQLAlchemy. Start with an empty workspace and provide a normal installable Python package. The task checks deterministic public configuration, migration-operation objects, offline SQL generation, and generic script-directory creation. It does not require a live database server or a network connection.

# Natural Language Instruction

Create the `alembic` project from an empty `workspace/`. Build an installable implementation, not a loose demonstration script. The public API guide below is the complete source of the task contract; preserve its import paths, signatures, return shapes, ordering, state changes, and exceptions.

Required capabilities:
- configuration and option access: implement the documented public behavior and preserve its input/output and error contract.
- offline migration context: implement the documented public behavior and preserve its input/output and error contract.
- migration operation objects and reversals: implement the documented public behavior and preserve its input/output and error contract.
- local generic script-directory commands: implement the documented public behavior and preserve its input/output and error contract.

Do not copy an upstream checkout or tests. Keep behavior deterministic and local, and make the package usable from the installation layout described below. The principal public entry points include: `get_main_option(name, default=None)`, `set_main_option(name, value)`, `get_section_option(section, name, default=None)`, `set_section_option(section, name, value)`.

# Supports

- Python 3.10 or later and SQLAlchemy-compatible public APIs.
- `alembic`, `alembic.config`, `alembic.command`, `alembic.runtime.migration`, `alembic.operations`, and `alembic.script` imports.
- Programmatic `Config` objects and ordinary `.ini` configuration files.
- Offline migration SQL for SQLite and PostgreSQL, generated into a caller-provided text buffer.
- Local filesystem migration environments created with the built-in `generic` template.


## NoNetwork boundary

Agent, candidate, verifier, Oracle, controls, and normal runtime execution are network-isolated. Do not access GitHub, package registries, Go proxies, DNS, or external services during execution; use only the frozen local build inputs.

# Project Directory Structure

```text
workspace/
├── pyproject.toml
└── src/alembic/
    ├── __init__.py
    ├── config.py
    ├── command.py
    ├── operations/
    │   ├── __init__.py
    │   └── ops.py
    ├── runtime/migration.py
    ├── script/
    └── templates/generic/
```

# API Usage Guide

`alembic.config.Config(file_: str | os.PathLike | None = None, toml_file: str | os.PathLike | None = None, ini_section: str = "alembic", output_buffer: TextIO | None = None, stdout: TextIO = sys.stdout, cmd_opts: Namespace | None = None, config_args: Mapping[str, Any] = {}, attributes: dict[str, Any] | None = None)` represents Alembic configuration. `get_main_option(name, default=None)`, `set_main_option(name, value)`, `get_section_option(section, name, default=None)`, and `set_section_option(section, name, value)` read and mutate string options. `attributes` is a mutable dictionary for programmatic objects such as a connection. `print_stdout(text, *args)` writes a formatted line to its `stdout` stream.

`alembic.runtime.migration.MigrationContext.configure(connection=None, url=None, dialect_name=None, dialect=None, environment_context=None, dialect_opts=None, opts=None)` creates a migration context. With `opts={"as_sql": True, "output_buffer": stream}`, the context generates SQL without opening a database connection. A URL or `dialect_name` determines dialect-specific behavior.

`alembic.operations.Operations(context)` exposes migration directives including `create_table(table_name, *columns, **kw)`, `add_column(table_name, column, schema=None)`, `create_index(index_name, table_name, columns, unique=False, schema=None, **kw)`, `drop_table(table_name, schema=None, **kw)`, and `execute(sqltext, execution_options=None)`. In offline mode they append deterministic SQL to the configured output buffer.

Operation value classes live in `alembic.operations.ops`: `CreateTableOp.from_table(table)`, `AddColumnOp(table_name, column, schema=None, **kw)`, `CreateIndexOp(index_name, table_name, columns, unique=False, schema=None, **kw)`, `AlterColumnOp(table_name, column_name, **kw)`, and `UpgradeOps(ops=())`. Their public attributes describe the requested change; `reverse()` returns the corresponding reverse operation or operation container.

`alembic.command.init(config, directory, template="generic", package=False)` creates a local migration environment. `alembic.command.revision(config, message=None, autogenerate=False, sql=False, head="head", splice=False, branch_label=None, version_path=None, rev_id=None, depends_on=None, process_revision_directives=None)` creates a revision script. `alembic.script.ScriptDirectory.from_config(config)` resolves a configured script location and provides its revision map.

`alembic.util.rev_id()` returns a newly generated 12-character lowercase hexadecimal revision identifier. Its value is intentionally non-deterministic, but its shape is stable.

### Public signatures and values

The configuration methods accept string option names and values. `Config.get_main_option(name, default=None)` and `Config.get_section_option(section, name, default=None)` return a string or the supplied default; `set_main_option(name, value)` and `set_section_option(section, name, value)` return `None` and update later reads. `Config.attributes` is a mutable dictionary, and `print_stdout(text, *args)` formats text and writes it to the configured stdout stream.

`MigrationContext.configure(connection=None, url=None, dialect_name=None, dialect=None, environment_context=None, dialect_opts=None, opts=None)` returns a context. `as_sql=True` and an `output_buffer` select local SQL generation; `url` or `dialect_name` selects a dialect. `Operations(context)` returns a facade whose `create_table(table_name, *columns, **kw)`, `add_column(table_name, column, schema=None)`, `create_index(index_name, table_name, columns, unique=False, schema=None, **kw)`, `drop_table(table_name, schema=None, **kw)`, and `execute(sqltext, execution_options=None)` return operation results or append SQL to the configured buffer.

`CreateTableOp.from_table(table)`, `AddColumnOp(table_name, column, schema=None, **kw)`, `CreateIndexOp(index_name, table_name, columns, unique=False, schema=None, **kw)`, `AlterColumnOp(table_name, column_name, **kw)`, and `UpgradeOps(ops=())` preserve their public attributes. Their `reverse()` methods return the corresponding reverse operation. `command.init(config, directory, template="generic", package=False)` and `command.revision(config, message=None, autogenerate=False, sql=False, head="head", splice=False, branch_label=None, version_path=None, rev_id=None, depends_on=None, process_revision_directives=None)` write only to the requested local migration directory. `ScriptDirectory.from_config(config)` returns the configured script directory, and `rev_id()` returns a 12-character lowercase hexadecimal string.

The configuration object must preserve the selected `ini_section`, caller-provided `config_args`, and mutable `attributes`. A configured `output_buffer` receives SQL text in offline mode; no connection is opened when `as_sql` is true. Operation objects retain table, column, schema, index, and keyword values supplied by the caller, and reverse operations use the matching inverse directive. `command.init` creates the requested generic migration files locally and `ScriptDirectory.from_config` reads the configured location without contacting a database or service.

Normal option reads are deterministic for a fixed configuration and return the caller's default when a key is absent. SQL output is text written in operation order, and the selected SQLite or PostgreSQL dialect controls quoting and statement syntax. A revision with an explicit `rev_id` preserves that identifier; when omitted, the generated identifier remains a lowercase hexadecimal string of the documented length. Invalid dialect, malformed configuration, missing script locations, and unsupported operation arguments must surface as normal configuration, migration, or filesystem errors rather than being silently ignored.

# Implementation Notes

Preserve public import paths, signatures, option handling, SQL dialect behavior, operation reversal, and filesystem layout of the generic template. SQL must be produced locally; no test scenario permits connecting to a database service. The private verifier sends one bounded JSON request at a time to an unprivileged candidate subprocess and checks only normalized public results. Do not add task-specific commands, test fixtures, or network behavior.

# Examples

## Ordinary configuration

```python
from alembic.config import Config

config = Config()
config.set_main_option("script_location", "migrations")
assert config.get_main_option("script_location") == "migrations"
```

## Ordinary offline SQL

```python
from io import StringIO
from alembic.runtime.migration import MigrationContext
from alembic.operations import Operations

output = StringIO()
context = MigrationContext.configure(dialect_name="sqlite", opts={"as_sql": True, "output_buffer": output})
Operations(context).execute("SELECT 1")
```

## Boundary: missing option

```python
assert Config().get_main_option("missing", default="fallback") == "fallback"
```

## Boundary: local-only initialization

```python
from alembic import command

command.init(config, "migrations", template="generic")  # writes only below the requested local path
```

# Error Handling and Boundary Conditions

Reject invalid inputs using the documented exception or error result. Preserve empty-input behavior, ordering, Unicode/encoding behavior, cancellation or timeout semantics, and local filesystem boundaries where the API specifies them. Never turn a failed local operation into a network request, subprocess, or silent success.

Configuration files are read as text and option values remain strings unless an
API explicitly constructs a typed SQLAlchemy or migration object. A caller may
provide an in-memory `StringIO` buffer for offline output; the implementation
must not require a writable current directory for configuration-only use.
Operation directives must preserve the order in which they are submitted, and
their public reverse methods must not mutate the original operation. A missing
script directory or malformed option should produce a clear exception. Local
revision and template creation must stay below the directory selected by the
caller and must not invoke a shell command or contact a remote database.
