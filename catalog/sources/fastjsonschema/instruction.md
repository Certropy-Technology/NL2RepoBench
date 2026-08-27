# Project Description

Build `fastjsonschema`, a Python library that validates JSON-compatible data against JSON Schema drafts 04, 06, 07, and the supported 2019-09 subset. Start from an empty workspace and produce a normal installable Python package; do not copy verifier files or depend on this task's test directory.

## Supports

- Python 3.10 or newer, with no runtime dependency outside the standard library.
- The package import `fastjsonschema` and public functions `validate`, `compile`, and `compile_to_code`, plus documented exception classes and `VERSION`.
- JSON values only at this task boundary: objects, arrays, strings, numbers, booleans, and null. Validation may return a JSON value after applying documented defaults.
- Deterministic validation errors with public exception behavior. Do not make network requests while resolving references.

## API Usage Guide

`validate(definition: dict | bool, data, handlers: dict = {}, formats: dict = {}, use_default: bool = True, use_formats: bool = True, detailed_exceptions: bool = True, fast_fail: bool = True)` validates one JSON value. It returns the validated value, including applied defaults when enabled. An invalid value raises `JsonSchemaValueException` or `JsonSchemaValuesException`; an invalid schema raises `JsonSchemaDefinitionException`.

`compile(definition: dict | bool, handlers: dict = {}, formats: dict = {}, use_default: bool = True, use_formats: bool = True, detailed_exceptions: bool = True, fast_fail: bool = True)` returns a callable validator. Calling that validator with one JSON value has the same return, default, and exception behavior as `validate`.

`compile_to_code(definition: dict | bool, handlers: dict = {}, formats: dict = {}, use_default: bool = True, use_formats: bool = True, detailed_exceptions: bool = True, fast_fail: bool = True)` returns executable Python source as `str`. Executing the source defines a `validate` callable with equivalent JSON validation behavior; schema strings are treated as data and are not executed as Python.

The package root re-exports `JsonSchemaException`, `JsonSchemaValueException`, `JsonSchemaValuesException`, and `JsonSchemaDefinitionException`. `JsonSchemaException` derives from `ValueError`; the other three derive from it. `VERSION` is a public version string.

Handlers map URI schemes to child-local callables. The verifier supplies an allowlisted static `http`/`https` handler. Never fetch an unallowlisted URI. The JSON boundary cannot transport arbitrary Python callables; the complete callback contract is the two named recipes `is_identifier` and `is_ascii`, reconstructed inside the candidate child.

## Implementation Notes

Preserve JSON Schema ordering and default semantics, stable exceptions, nested references, regular expressions, and generated-code behavior. The private verifier keeps assertions outside the candidate and communicates through one unprivileged JSONL child process. Do not add a benchmark-specific server or CLI.

Upstream tests for arbitrary callbacks, non-JSON values, private code-generator internals, and optional formats are not silently claimed here; they are outside this explicit JSON-safe contract unless represented by the named recipes.
