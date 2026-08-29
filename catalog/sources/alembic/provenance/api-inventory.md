# Alembic API Inventory

Frozen source: `sqlalchemy/alembic` at `c116cbc0f39d9df2b4ce5f1871043a622ca8774f`.

| Area | Public symbols covered | Adaptation boundary |
| --- | --- | --- |
| Package/configuration | `alembic.__version__`, `Config`, option accessors, `attributes`, `print_stdout` | Child returns scalar options and buffered text. |
| Runtime context | `MigrationContext.configure` | Child returns selected dialect names and offline mode state. |
| Operation facade | `Operations.create_table`, `add_column`, `create_index`, `drop_table`, `execute` | Child returns bounded offline SQL strings; no DB connection is opened. |
| Operation objects | `CreateTableOp`, `AddColumnOp`, `CreateIndexOp`, `AlterColumnOp`, `UpgradeOps` | Child serializes public attributes and reverse-class names. |
| Commands/scripts | `command.init`, `command.revision`, `ScriptDirectory.from_config`, `util.rev_id` | Child uses a temporary local directory and returns file/layout metadata only. |

The task intentionally excludes live engine execution, autogeneration against a database, plugin entry points, interactive editing, and backend-specific integration suites because they require external services or non-JSON object graphs beyond this deterministic contract.
