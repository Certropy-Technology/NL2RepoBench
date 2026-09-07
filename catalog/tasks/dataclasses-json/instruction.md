# Project Description

Create an installable Python package named `dataclasses-json`. It should add a
small, predictable JSON serialization API to standard-library dataclasses. A
user must be able to decorate a dataclass, convert instances to JSON-compatible
Python values or JSON text, and reconstruct instances from either form.

This task intentionally specifies a stable behavior subset. Do not infer a
larger API or copy an upstream test suite. The evaluator uses a JSON-only
subprocess boundary and does not require callbacks, arbitrary Marshmallow
fields, global mutable encoders, generic dataclasses, unions, or dynamic type
resolution.

## Supports

- Python 3.10 or newer, with Python 3.12 supported.
- The project must be installable with `python -m pip install .` from a clean
  workspace. Include a normal `pyproject.toml` and package metadata.
- Runtime dependencies may be declared, but the package must work offline once
  its declared dependencies are installed. The reference environment provides
  `marshmallow==3.19.0`, `typing-inspect==0.9.0`, and their pinned transitive
  wheels.
- Public imports are from `dataclasses_json`.

## Natural Language Instruction

Create the installable `dataclasses-json` project from an empty workspace.
Implement the decorator/mixin serialization API, field naming and exclusion,
unknown-field policies, nested dataclass reconstruction, and the schema
facade described below. Keep output JSON-compatible and deterministic.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── README.md
└── dataclasses_json/
    ├── __init__.py
    ├── api.py
    ├── cfg.py
    ├── core.py
    ├── schema.py
    └── py.typed
```

The root package exports `dataclass_json`, `DataClassJsonMixin`, configuration
helpers, enum policies, and `__version__`; these are the only project files an
agent needs to create.

## API Usage Guide

### `dataclass_json`

`dataclass_json` is usable as either `@dataclass_json` or
`@dataclass_json(letter_case=LetterCase.CAMEL)`. Apply it after
`@dataclass` (the dataclass decorator is closest to the class). It adds these
callable methods to the class:

```python
to_dict(self, encode_json=False) -> dict
to_json(self, *, ensure_ascii=True, indent=None, sort_keys=False, **json_options) -> str
from_dict(cls, values: dict, *, infer_missing=False) -> object
from_json(cls, text: str, *, infer_missing=False, **json_options) -> object
schema(cls, *, many=False, **options)
```

`to_dict()` returns JSON-compatible dictionaries, lists, strings, numbers,
booleans, and null. Nested dataclasses, lists, tuples, dictionaries, enums, and `Optional` values
should be handled in the ordinary JSON representation. Temporal values are
outside this task subset. `to_json()` returns valid JSON;
`ensure_ascii=False` preserves Unicode and `sort_keys=True` sorts object keys.
Round trips preserve the declared dataclass fields and values.

`from_dict()` accepts a JSON-compatible dictionary and reconstructs the declared
field types, including nested dataclasses, containers, enums, optional values, and defaults. Missing fields with dataclass defaults
use those defaults. With `infer_missing=True`, a missing optional field becomes
`None`; a missing required field remains an error. Invalid JSON text or a
non-object top-level value is an error.

### Field configuration and case conversion

`config(field_name="...")` can be passed as a field's `metadata` to choose its
wire name. `config(exclude=Exclude.ALWAYS)` omits a field from serialization;
`Exclude.NEVER` keeps it. `LetterCase.CAMEL` converts snake_case field names to
camelCase, and `LetterCase.KEBAB` converts them to kebab-case. Explicit
`field_name` takes precedence over class-level case conversion.

### Unknown fields

`Undefined.RAISE` rejects unknown input keys. `Undefined.EXCLUDE` ignores them.
`Undefined.INCLUDE` requires one field annotated as `CatchAll` (a dictionary)
and stores unknown keys there; those keys are emitted again by `to_dict()`.

### Other exports

Export `DataClassJsonMixin`, `config`, `global_config`, `Exclude`, `CatchAll`,
`Undefined`, `LetterCase`, and `__version__` from the package root. `schema()`
must return a usable Marshmallow schema for the decorated class; its `dump()`
and `load()` methods must support one object, and `many=True` must support a
list of objects.

## Implementation Notes

Keep serialization JSON-safe at public boundaries: no Python object identity,
class objects, or non-JSON sentinels may be required in caller data. Preserve
dataclass defaults and field ordering. Raise ordinary, inspectable exceptions
for malformed input rather than silently returning a partial object. The
package should expose a version and type annotations, and should not require
 the upstream repository, its tests, or network access at runtime.

## Examples

```python
from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class Point:
    x: int
    y: int

point = Point.from_json('{"x": 1, "y": 2}')
assert point.to_dict() == {"x": 1, "y": 2}
```

```python
payload = Point(3, 4).to_json(sort_keys=True)
assert Point.from_json(payload).x == 3
```

## Error Handling and Boundary Conditions

Malformed JSON and a non-object top-level value passed to `from_json` must
raise an inspectable exception. `Undefined.RAISE` rejects unknown keys,
`Undefined.EXCLUDE` ignores them, and `Undefined.INCLUDE` requires a `CatchAll`
field. Preserve Unicode when `ensure_ascii=False`; do not silently drop fields.
