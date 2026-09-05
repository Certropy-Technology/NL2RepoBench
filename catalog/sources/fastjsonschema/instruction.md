# Project Description

Build `fastjsonschema`, a Python library that validates JSON-compatible data against JSON Schema drafts 04, 06, 07, and the supported 2019-09 subset. Start from an empty workspace and produce a normal installable Python package; do not copy verifier files or depend on this task's test directory.

## Natural Language Instruction

Create the installable `fastjsonschema` package from an empty workspace.
Implement validation, compiler, generated-code, defaults, formats, references,
and deterministic exception behavior described below.

## Supports or Environment Configuration

- Use CPython 3.12 and the exact metadata in `task.toml`; runtime behavior uses
  only the standard library and never resolves references over the network.
- Agent, candidate, verifier, Oracle, and controls run with no network access.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
└── fastjsonschema/
    ├── __init__.py
    ├── draft04.py
    ├── draft06.py
    ├── draft07.py
    ├── draft2019-09.py
    └── exceptions.py
```

## API Usage Guide

The API Usage Guide below is authoritative for all signatures, JSON domains,
return values, defaults, generated source, and exception classes.

## Implementation Notes

Keep validation deterministic and treat schemas as data. Generated code must
not execute schema-provided strings as Python.

## Detailed Implementation Nodes

The implementation is organized around the package root and the three public
operations. `validate` may delegate to a compiled validator, but it must return
the input value (or the value after documented defaults) rather than a private
wrapper. `compile` returns a reusable callable whose later calls do not mutate
the schema. `compile_to_code` returns ordinary Python source as text; generated
source must carry enough local data to validate the supplied schema without
reading files or resolving a URL at runtime.

Schema keywords are evaluated against JSON-compatible objects, arrays, strings,
numbers, booleans, and null. Preserve JSON Schema type distinctions, including
that booleans are not integers for validation purposes. Object properties,
required keys, array items, numeric bounds, string patterns, enum/const values,
combinators, `$ref`, defaults, and supported formats must use deterministic
exception paths and messages. A caller-provided format/handler mapping is read
only; named callback recipes are reconstructed inside the child boundary.

## Examples

```python
import fastjsonschema

schema = {'type': 'object', 'properties': {'id': {'type': 'integer'}},
          'required': ['id']}
check = fastjsonschema.compile(schema)
check({'id': 7})  # {'id': 7}
```

```python
import fastjsonschema

source = fastjsonschema.compile_to_code({'type': 'array',
                                         'items': {'type': 'string'}})
assert isinstance(source, str)
```

```python
from fastjsonschema import JsonSchemaValueException, validate

try:
    validate({'type': 'integer'}, 'seven')
except JsonSchemaValueException:
    pass
```

## Error Handling and Boundary Conditions

- Invalid schemas raise `JsonSchemaDefinitionException`; invalid data raises
  `JsonSchemaValueException` or `JsonSchemaValuesException` according to the
  configured detail and aggregation behavior.
- `compile_to_code` must never execute schema-provided strings as Python. URI
  references are resolved only through the supplied local/allowlisted handler;
  missing or forbidden references fail closed.
- Empty objects and arrays, explicit false schemas, defaults, duplicate object
  keys, nested references, and unsupported non-JSON values follow the stated
  JSON-safe contract without relying on process-global mutable state.

## Detailed Implementation Nodes

The implementation is organized around the package root and the three public
operations. `validate` may delegate to a compiled validator, but it must return
the input value (or the value after documented defaults) rather than a private
wrapper. `compile` returns a reusable callable whose later calls do not mutate
the schema. `compile_to_code` returns ordinary Python source as text; generated
source must carry enough local data to validate the supplied schema without
reading files or resolving a URL at runtime.

Schema keywords are evaluated against JSON-compatible objects, arrays, strings,
numbers, booleans, and null. Preserve JSON Schema type distinctions, including
that booleans are not integers for validation purposes. Object properties,
required keys, array items, numeric bounds, string patterns, enum/const values,
combinators, `$ref`, defaults, and supported formats must use deterministic
exception paths and messages. A caller-provided format/handler mapping is read
only; named callback recipes are reconstructed inside the child boundary.

## Examples

```python
import fastjsonschema

schema = {'type': 'object', 'properties': {'id': {'type': 'integer'}},
          'required': ['id']}
check = fastjsonschema.compile(schema)
check({'id': 7})  # {'id': 7}
```

```python
import fastjsonschema

source = fastjsonschema.compile_to_code({'type': 'array',
                                         'items': {'type': 'string'}})
assert isinstance(source, str)
```

```python
from fastjsonschema import JsonSchemaValueException, validate

try:
    validate({'type': 'integer'}, 'seven')
except JsonSchemaValueException:
    pass
```

## Error Handling and Boundary Conditions

- Invalid schemas raise `JsonSchemaDefinitionException`; invalid data raises
  `JsonSchemaValueException` or `JsonSchemaValuesException` according to the
  configured detail and aggregation behavior.
- `compile_to_code` must never execute schema-provided strings as Python. URI
  references are resolved only through the supplied local/allowlisted handler;
  missing or forbidden references fail closed.
- Empty objects and arrays, explicit false schemas, defaults, duplicate object
  keys, nested references, and unsupported non-JSON values follow the stated
  JSON-safe contract without relying on process-global mutable state.

## Examples

```python
import fastjsonschema
fastjsonschema.validate({"type": "string"}, "ok")
```

```python
check = fastjsonschema.compile({"type": "integer"})
check(3)
```

## Error Handling and Boundary Conditions

```python
fastjsonschema.validate({"type": "string"}, 1)
```

```python
fastjsonschema.compile_to_code({"type": "null"})
```

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
