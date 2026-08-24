# Project Description

Build `fastjsonschema`, a Python library that validates JSON-compatible data against JSON Schema drafts 04, 06, 07, and the supported 2019-09 subset. Start from an empty workspace and produce a normal installable Python package; do not copy verifier files or depend on this task's test directory.

## Supports

- Python 3.10 or newer, with no runtime dependency outside the standard library.
- The package import `fastjsonschema` and public functions `validate`, `compile`, and `compile_to_code`, plus documented exception classes and `VERSION`.
- JSON values only at this task boundary: objects, arrays, strings, numbers, booleans, and null. Validation may return a JSON value after applying documented defaults.
- Deterministic validation errors with public exception behavior. Do not make network requests while resolving references.

## API Usage Guide

`validate(schema, data, handlers={}, formats={}, use_default=True, use_formats=True, detailed_exceptions=True, fast_fail=True)` validates one JSON value and returns the value or raises a public schema exception. `compile` returns a callable validator with the same options. `compile_to_code` returns executable Python source defining `validate`; generated source validates the same JSON values and does not execute schema text as Python.

Handlers map URI schemes to child-local callables. The verifier supplies an allowlisted static `http`/`https` handler. Never fetch an unallowlisted URI. The JSON boundary cannot transport arbitrary Python callables; the complete callback contract is the two named recipes `is_identifier` and `is_ascii`, reconstructed inside the candidate child.

## Implementation Notes

Preserve JSON Schema ordering and default semantics, stable exceptions, nested references, regular expressions, and generated-code behavior. The private verifier keeps assertions outside the candidate and communicates through one unprivileged JSONL child process. Do not add a benchmark-specific server or CLI.

Upstream tests for arbitrary callbacks, non-JSON values, private code-generator internals, and optional formats are not silently claimed here; they are outside this explicit JSON-safe contract unless represented by the named recipes.
