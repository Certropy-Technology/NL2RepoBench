# python-json-logger

## Project Description

Build an installable `python-json-logger` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution identity: `python-json-logger`; public import package begins at `pythonjsonlogger`.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `Root and compatibility modules`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `JsonFormatter`: preserve the documented object or module behavior, including state and side effects.
3. `BaseJsonFormatter` and helpers`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `python-json-logger`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- CPython 3.12.14 on the pinned Linux image.
- Distribution identity: `python-json-logger`; public import package begins at `pythonjsonlogger`.
- Install from the workspace with `python -m pip install .`; do not download packages during evaluation.
- Declared build/runtime packages are supplied by the frozen evaluation image: `setuptools==80.9.0`
- Build metadata and package data must be present in the workspace and agree with the public import paths below.
- Agent, candidate, evaluator, Oracle, and control execution are network-isolated. Do not access GitHub, package registries, DNS, databases, or external services at runtime.
- Use deterministic local inputs. Do not rely on the current wall clock, host-specific absolute paths, undeclared environment variables, or an installed copy of the target package.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── an/
│   ├── __init__.py
│   └── (public modules documented in API Usage Guide)
```

The tree lists agent-owned public project files only. Add additional public modules when required by the API Usage Guide, but keep their import paths consistent with package metadata. Do not create evaluator-only files, hidden fixtures, or private reports in the generated project.

## API Usage Guide

The following is the task-specific public contract recovered from the local instruction and inventory. For every function, class, method, constant, export, and command named below, preserve its complete signature, accepted input domain, return type and shape, ordering, determinism, state/side effects, exceptions, and examples. When the source contract gives an optional argument or a compatibility alias, it is part of the required surface.

## Root and compatibility modules

`pythonjsonlogger.ORJSON_AVAILABLE` and `pythonjsonlogger.MSGSPEC_AVAILABLE` are booleans indicating whether the optional modules can be imported. The package exposes the modules `core`, `defaults`, `exception`, `json`, `jsonlogger`, and `utils`. The compatibility module `pythonjsonlogger.jsonlogger` re-exports `JsonFormatter` and emits a `DeprecationWarning` when imported.

## `JsonFormatter`

Import `JsonFormatter` from `pythonjsonlogger.json`. It is a `logging.Formatter` subclass with the constructor:

```python
JsonFormatter(
    fmt=None, datefmt=None, style="%", validate=True, *, prefix="",
    rename_fields=None, rename_fields_keep_missing=False, static_fields=None,
    reserved_attrs=None, timestamp=False, defaults=None,
    exc_info_as_array=False, stack_info_as_array=False,
    json_default=None, json_encoder=None, json_serializer=json.dumps,
    json_indent=None, json_ensure_ascii=True, **kwargs
)
```

With no format, a normal record produces an object containing `message`. A string format extracts named logging fields using percent (`%(levelname)s`), brace (`{levelname}`), template (`$levelname`), or comma-separated (`style=","`) syntax. A list or tuple of names is also accepted. Field order follows the requested format and insertion order. Missing format fields have a `None` value; invalid styles raise `ValueError`.

`defaults` supplies fields before record data and record/extra values override them. `static_fields` adds constant values. `rename_fields` maps output keys once, preserving order; `rename_fields_keep_missing=True` emits missing target keys as `None`. `prefix` is prepended to the serialized JSON text. `timestamp=True` adds UTC ISO-8601 text under `timestamp`; a string value selects that output key.

When `record.msg` is a mapping, its entries are merged into the output and the formatted `message` is an empty string. The caller's mapping remains unchanged when exception or stack information is added. Extra record attributes are included unless reserved or private. `json_ensure_ascii` defaults to true, while false preserves Unicode characters. `json_indent` is passed to the serializer.

`formatException` and `formatStack` return strings by default and lists of lines when their corresponding `*_as_array` option is true. `process_log_record(log_data)` is an override hook that may add or transform fields before serialization. `json_serializer` is called with the final mapping and `default`, `cls`, `indent`, and `ensure_ascii` keyword arguments.

## `BaseJsonFormatter` and helpers

`pythonjsonlogger.core.BaseJsonFormatter` is the shared `logging.Formatter` base. Its `jsonify_log_record(log_data)` method raises `NotImplementedError` unless implemented by a concrete formatter. `RESERVED_ATTRS` is a sorted list of standard `LogRecord` attributes, including `taskName` on Python 3.12. `merge_record_extra(record, target, reserved, rename_fields=None)` mutates and returns `target`, copying non-reserved, non-private record attributes and applying one-step key renames.

`pythonjsonlogger.defaults` provides deterministic JSON fallback helpers. Datetimes and dates use `isoformat()`, UUIDs use their hyphenated string, bytes and bytearrays use standard base64, dataclasses become dictionaries, exceptions become `ClassName: message`, enum values are encoded recursively, classes use their `__name__`, and unknown objects fall back to `str`, then `repr`, then `__could_not_encode__`.

`pythonjsonlogger.utils.package_is_available(name, throw_error=False, extras_name=None)` returns whether an importable package exists. With `throw_error=True`, a missing package raises `MissingPackageError` whose message identifies the package and optional extra name.


Preserve standard `logging.Formatter` behavior, deterministic field ordering, JSON types, and exception text. Use a separate installable package and do not import candidate code into separate evaluator code. The optional format backends are not required for the core task and must not be fetched at runtime. Keep compatibility imports and deprecation warnings observable without requiring network, current time, or machine-specific paths.

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
JsonFormatter(
    fmt=None, datefmt=None, style="%", validate=True, *, prefix="",
    rename_fields=None, rename_fields_keep_missing=False, static_fields=None,
    reserved_attrs=None, timestamp=False, defaults=None,
    exc_info_as_array=False, stack_info_as_array=False,
    json_default=None, json_encoder=None, json_serializer=json.dumps,
    json_indent=None, json_ensure_ascii=True, **kwargs
)
```

### Example 2: ordinary usage
```text
JsonFormatter(
    fmt=None, datefmt=None, style="%", validate=True, *, prefix="",
    rename_fields=None, rename_fields_keep_missing=False, static_fields=None,
    reserved_attrs=None, timestamp=False, defaults=None,
    exc_info_as_array=False, stack_info_as_array=False,
    json_default=None, json_encoder=None, json_serializer=json.dumps,
    json_indent=None, json_ensure_ascii=True, **kwargs
)
```

### Example 3: boundary or error behavior
```text
JsonFormatter(
    fmt=None, datefmt=None, style="%", validate=True, *, prefix="",
    rename_fields=None, rename_fields_keep_missing=False, static_fields=None,
    reserved_attrs=None, timestamp=False, defaults=None,
    exc_info_as_array=False, stack_info_as_array=False,
    json_default=None, json_encoder=None, json_serializer=json.dumps,
    json_indent=None, json_ensure_ascii=True, **kwargs
)
```

### Example 4: boundary or error behavior
```text
JsonFormatter(
    fmt=None, datefmt=None, style="%", validate=True, *, prefix="",
    rename_fields=None, rename_fields_keep_missing=False, static_fields=None,
    reserved_attrs=None, timestamp=False, defaults=None,
    exc_info_as_array=False, stack_info_as_array=False,
    json_default=None, json_encoder=None, json_serializer=json.dumps,
    json_indent=None, json_ensure_ascii=True, **kwargs
)
```


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
