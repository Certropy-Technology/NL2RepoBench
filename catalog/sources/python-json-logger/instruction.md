# Project Description

Build an installable Python distribution named `python-json-logger` from an empty workspace. It provides logging formatters that turn standard-library `logging.LogRecord` values into deterministic JSON text, with configurable fields, aliases, defaults, static metadata, timestamps, and structured exception information.

# Supports

- Python 3.12 on Linux with a PEP 517 `pyproject.toml` and an installable `src` or flat package layout.
- Distribution name `python-json-logger`, version `4.2.0`, and import package `pythonjsonlogger`.
- The standard-library JSON implementation is required. Optional `orjson` and `msgspec` integrations may be absent; expose availability flags accurately and report their missing-package behavior.
- Runtime operation is local and synchronous. Candidate code, the verifier, and controls run without network access or external services.

# API Usage Guide

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

# Implementation Notes

Preserve standard `logging.Formatter` behavior, deterministic field ordering, JSON types, and exception text. Use a separate installable package and do not import candidate code into trusted verifier code. The optional format backends are not required for the core task and must not be fetched at runtime. Keep compatibility imports and deprecation warnings observable without requiring network, current time, or machine-specific paths.
