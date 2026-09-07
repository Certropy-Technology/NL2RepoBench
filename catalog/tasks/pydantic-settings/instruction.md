# pydantic-settings

## Project Description

Build an installable `pydantic-settings` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution identity: `pydantic-settings`; public import package begins at `pydantic_settings`.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `BaseSettings`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `Dotenv and secrets`: preserve the documented object or module behavior, including state and side effects.
3. `SettingsConfigDict`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `CliApp`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- CPython 3.12 on the pinned Linux image.
- Distribution identity: `pydantic-settings`; public import package begins at `pydantic_settings`.
- Install from the workspace with `python -m pip install .`; do not download packages during evaluation.
- Declared build/runtime packages are supplied by the frozen evaluation image: `annotated-types==0.7.0`, `editables==0.5`, `hatchling==1.28.0`, `packaging==26.0`, `pathspec==1.0.4`, `pluggy==1.6.0`, `pydantic==2.13.4`, `pydantic-core==2.46.4`, `python-dotenv==1.2.2`, `setuptools==80.9.0`, `trove-classifiers==2026.6.1.19`, `typing-extensions==4.15.0`, `typing-inspection==0.4.4`, `wheel==0.45.1`
- Build metadata and package data must be present in the workspace and agree with the public import paths below.
- Agent, candidate, evaluator, Oracle, and control execution are network-isolated. Do not access GitHub, package registries, DNS, databases, or external services at runtime.
- Use deterministic local inputs. Do not rely on the current wall clock, host-specific absolute paths, undeclared environment variables, or an installed copy of the target package.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── different/
│   ├── __init__.py
│   └── (public modules documented in API Usage Guide)
```

The tree lists agent-owned public project files only. Add additional public modules when required by the API Usage Guide, but keep their import paths consistent with package metadata. Do not create evaluator-only files, hidden fixtures, or private reports in the generated project.

## API Usage Guide

The following is the task-specific public contract recovered from the local instruction and inventory. For every function, class, method, constant, export, and command named below, preserve its complete signature, accepted input domain, return type and shape, ordering, determinism, state/side effects, exceptions, and examples. When the source contract gives an optional argument or a compatibility alias, it is part of the required surface.

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


- Source loading must be deterministic and must not mutate `os.environ`.
- Preserve Pydantic validation aliases and nested model validation during source merging.
- JSON decoding is a source concern: scalar strings are passed to Pydantic, while complex values are decoded before validation unless `NoDecode` applies.
- Keep all package behavior local and deterministic. No network access is needed at runtime.

## Implementation Notes

- Keep the root exports and module paths stable after installation; do not make behavior depend on the repository's current directory.
- Preserve explicit ordering guarantees. When the contract does not promise an order, do not introduce a new observable order accidentally.
- Propagate documented exceptions and avoid replacing them with generic errors. Validate malformed, empty, boundary, and repeated inputs as described by the API contract.
- Keep filesystem, process, terminal, and resource effects bounded and local. Close files and other resources on both success and failure.
- Do not copy an upstream checkout, implementation source, or evaluation-only material into the generated project. Implement the public behavior from this specification.

## Examples

The examples below are retained from the local task specification. They are starting points for ordinary calls and boundary/error behavior; their exact output and exception semantics remain governed by the API Usage Guide.

### Example 1: ordinary usage
```text
class BaseSettings(pydantic.BaseModel): ...
```

### Example 2: ordinary usage
```text
class SettingsConfigDict(pydantic.ConfigDict, total=False): ...
```

### Example 3: boundary or error behavior
```text
CliApp.run(model_cls, cli_args=None, cli_cmd_method_name='cli_cmd', **model_init_data)
CliApp.serialize(model, list_style='json', dict_style='json', positionals_first=False) -> list[str]
```

### Example 4: boundary or error behavior
```text
class BaseSettings(pydantic.BaseModel): ...
```


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
