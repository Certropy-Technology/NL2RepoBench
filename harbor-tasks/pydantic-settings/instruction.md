# Project Description

Create an installable Python package named `pydantic-settings`. It provides typed application configuration by combining Pydantic model validation with initialization values, environment variables, dotenv files, and file secrets. The implementation in this task is limited to the local core API described below; cloud secret providers are outside scope.

# Supports

- Python 3.10 or newer.
- A root `pyproject.toml` using package name `pydantic-settings` and an importable `pydantic_settings` package.
- Runtime dependencies: `pydantic>=2.7.0`, `python-dotenv>=0.21.0`, and `typing-inspection>=0.4.0`.
- Editable installation with `python -m pip install -e .`.
- Public imports: `BaseSettings`, `SettingsConfigDict`, `SettingsError`, `NoDecode`, `ForceDecode`, `CliApp`, `CliPositionalArg`, and `CliSubCommand` from `pydantic_settings`.

# API Usage Guide

## `BaseSettings`

```python
class BaseSettings(pydantic.BaseModel): ...
```

Subclasses declare fields like Pydantic models. Construction validates merged settings data and supports normal Pydantic methods such as `model_dump()`. Missing required fields and invalid values raise `pydantic.ValidationError`. Extra initialization values follow the model's Pydantic `extra` configuration.

The constructor accepts ordinary field values plus keyword-only controls including `_case_sensitive`, `_env_prefix`, `_env_file`, `_env_file_encoding`, `_env_file_depth`, `_env_ignore_empty`, `_env_nested_delimiter`, `_env_nested_max_split`, `_env_parse_none_str`, `_env_parse_enums`, `_cli_parse_args`, `_cli_exit_on_error`, and `_secrets_dir`. Equivalent persistent values may be declared through `model_config = SettingsConfigDict(...)`.

Sources have this default highest-to-lowest precedence: initialization values, process environment, dotenv file, secret files, then field defaults. Values from different sources are deep-merged for nested mappings while earlier sources keep precedence. Override `settings_customise_sources(settings_cls, init_settings, env_settings, dotenv_settings, file_secret_settings)` to return a different order.

Environment names are case-insensitive by default. `env_prefix` prepends a string to field names. A field validation alias is considered as an environment name; with `populate_by_name=True`, its field name is also accepted and the alias wins when both exist. When `env_ignore_empty=True`, empty values are omitted. Complex values such as lists, sets, dictionaries, and nested models are JSON-decoded. Invalid JSON for a complex field raises `SettingsError` identifying the field and source.

`env_nested_delimiter` expands flat names into nested data. For example, `APP_DB__HOST=x` with prefix `APP_` and delimiter `__` populates `db.host`. A nested value overrides the corresponding key from a top-level JSON value. `env_nested_max_split` limits delimiter splits.

`env_parse_none_str` converts the configured exact string to `None`; `env_parse_enums=True` accepts enum member names. Annotating a field with `NoDecode` suppresses automatic JSON decoding. Annotating with `ForceDecode` requests JSON decoding even when decoding is otherwise disabled.

## Dotenv and secrets

`env_file` is a path or sequence of paths parsed with python-dotenv. Later files override earlier files. Process environment still has higher precedence. `secrets_dir` is a directory or sequence of directories where each filename is a settings key and stripped file content is its value. Missing secret directories emit a warning rather than failing construction. Dotenv has higher default precedence than secrets.

## `SettingsConfigDict`

```python
class SettingsConfigDict(pydantic.ConfigDict, total=False): ...
```

This typed dictionary accepts Pydantic model configuration plus settings keys including `env_prefix`, `env_file`, `env_ignore_empty`, `env_nested_delimiter`, `env_nested_max_split`, `env_parse_none_str`, `env_parse_enums`, and `secrets_dir`.

## `CliApp`

```python
CliApp.run(model_cls, cli_args=None, cli_cmd_method_name='cli_cmd', **model_init_data)
CliApp.serialize(model, list_style='json', dict_style='json', positionals_first=False) -> list[str]
```

`run` accepts a `BaseSettings`, Pydantic `BaseModel`, or Pydantic dataclass class, parses CLI values, constructs it, and invokes its `cli_cmd` method when present. It supports synchronous and asynchronous methods, including calls made while an event loop is already running. Invalid non-Pydantic classes raise `SettingsError`. `CliPositionalArg[T]` marks positional fields and `CliSubCommand[T]` marks optional nested subcommands.

`serialize` emits only non-default values. Its output can be passed back to `run` to reconstruct the model. `list_style` supports `json`, repeated `argparse` flags, and comma-separated `lazy`; `dict_style` supports JSON or repeated `key=value` values. Optional argument names use kebab case for plain Pydantic models run through `CliApp` and preserve configured settings behavior for `BaseSettings`.

# Implementation Notes

- Source loading must be deterministic and must not mutate `os.environ`.
- Preserve Pydantic validation aliases and nested model validation during source merging.
- JSON decoding is a source concern: scalar strings are passed to Pydantic, while complex values are decoded before validation unless `NoDecode` applies.
- Keep all package behavior local and deterministic. No network access is needed at runtime.
