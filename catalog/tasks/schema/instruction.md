# Project Description

Build `schema`, an installable pure-Python library for validating and
transforming nested Python data structures. A schema may be a literal, type,
predicate, object with `validate`, mapping, container of alternatives, or a
composition made with the public helpers below. Successful validation returns
the validated value, including transformations; failure raises `SchemaError`
or one of its documented subclasses.

The scored contract is intentionally bounded to deterministic in-memory
validation, defaults, hooks, errors, JSON input, and draft-07 JSON Schema
generation. It excludes file/network validation, CLI behavior, static typing,
performance, and JSON Schema features not described here.

# Supports

- CPython 3.12 on Debian 12 `linux/amd64`.
- An installable distribution and import package named `schema`, version
  `0.7.8`.
- No required third-party runtime dependency on Python 3.12. Build tooling is
  preinstalled and must not be fetched at runtime.
- A local source build installable with `pip --no-deps --no-build-isolation`.
- No runtime network, subprocess, external service, database, or native
  extension behavior.

`schema.__version__` is `"0.7.8"`. `schema.__all__` contains exactly these
names, in order:

```python
[
    "Schema", "And", "Or", "Regex", "Optional", "Use", "Forbidden",
    "Const", "Literal", "SchemaError", "SchemaWrongKeyError",
    "SchemaMissingKeyError", "SchemaForbiddenKeyError",
    "SchemaUnexpectedTypeError", "SchemaOnlyOneAllowedError",
]
```

`Hook` is also importable from `schema`, but is not in `__all__`.

# API Usage Guide

## Errors

```python
SchemaError(autos, errors=None)
SchemaWrongKeyError(SchemaError)
SchemaMissingKeyError(SchemaError)
SchemaForbiddenKeyError(SchemaError)
SchemaUnexpectedTypeError(SchemaError)
SchemaOnlyOneAllowedError(SchemaError)
```

`SchemaError.autos` and `.errors` are lists; scalar constructor arguments are
wrapped in one-element lists. The read-only `code` property removes `None` and
duplicate strings from each list while preserving order. It joins explicit
`errors` with newlines when any exist, otherwise it joins `autos`.
`str(error)` and the first exception argument equal `code`.

Wrong extra mapping keys, missing required keys, forbidden keys, direct type
mismatches, and multiple `only_one` keys use their corresponding subclasses.
Nested value failures are wrapped in `SchemaError` with one `Key '<key>'
error:` line per mapping level. A `Schema(..., error=text)` explicit message
takes precedence in `code`; every helper accepting `error` supports `{}`
formatting with the rejected data.

## `Schema`

```python
Schema(
    schema,
    error=None,
    ignore_extra_keys=False,
    name=None,
    description=None,
    as_reference=False,
)

schema.validate(data, **kwargs)
schema.is_valid(data, **kwargs) -> bool
schema.json_schema(schema_id, use_refs=False, **kwargs) -> dict
```

Properties expose `schema`, `name`, `description`, and `ignore_extra_keys`.
`repr(Schema(value))` is `Schema(<value repr>)`. `as_reference=True` without a
name raises `ValueError("Schema used as reference should have a name")`.

Validation dispatch follows these rules:

- A literal compares with `==` and returns the original data on equality.
- A type requires `isinstance(data, type)` and returns data. Booleans do not
  satisfy an `int` schema. Failure raises `SchemaUnexpectedTypeError` with
  `"<data repr> should be instance of '<type name>'"`.
- A callable is invoked with data. Truthy return keeps the original data;
  false return raises `SchemaError`. A raised `SchemaError` is propagated into
  the error lists; another exception is wrapped with its type and repr.
- An object with `validate` is called as `obj.validate(data, **kwargs)`.
- A `list`, `tuple`, `set`, or `frozenset` schema requires the same container
  type. Every element must match at least one schema element, and the returned
  container preserves the input container type. Empty input containers pass.
- A mapping validates keys and values and returns the same mapping subtype when
  constructible. Schema keys are prioritized so literal/forbidden keys beat
  broad type keys, and optionals beat type keys.

For mappings, every non-optional schema key must match. Missing keys raise
`SchemaMissingKeyError` beginning `Missing key:` or `Missing keys:`. Unmatched
input keys raise `SchemaWrongKeyError` beginning `Wrong key` or `Wrong keys`.
With `ignore_extra_keys=True`, unmatched keys are omitted from the returned
mapping, recursively. A broad `{object: object}` entry explicitly validates and
retains extra keys.

`is_valid` calls `validate` and returns `False` only for `SchemaError`; it does
not return transformed data. A non-empty name prefixes generated errors as
`'<name>' <message>`.

Example:

```python
from schema import And, Optional, Schema, Use

person = Schema({
    "name": And(str, len),
    "age": And(Use(int), lambda n: 0 < n < 130),
    Optional("active", default=True): bool,
})
assert person.validate({"name": "Ada", "age": "37"}) == {
    "name": "Ada", "age": 37, "active": True,
}
```

## Combinators and validators

```python
And(*schemas, error=None, ignore_extra_keys=False, schema=None)
Or(*schemas, only_one=False, error=None, ignore_extra_keys=False, schema=None)
Regex(pattern_str, flags=0, error=None)
Use(callable_, error=None)
Const(schema, ...)
```

`And.validate` validates from left to right, feeding each transformed result to
the next schema. `And.args` is the original tuple. `Or.validate` tries in
argument order and returns the first success; if all fail, it raises an
aggregate `SchemaError` beginning `<Or repr> did not validate <data repr>`.
An empty `Or` always fails.

When an `Or(..., only_one=True)` is used as a mapping key, exactly one of its
alternatives may be present. Multiple matches raise
`SchemaOnlyOneAllowedError`; match state is reset after each mapping validation
and independent copied/nested alternatives do not leak state.

`Regex` compiles with `re.compile`, searches rather than full-matches, exposes
`pattern_str`, and returns the input string on success. A mismatch or a
non-string/buffer value raises `SchemaError`; an invalid pattern raises the
normal `re.compile` error. Its repr includes the pattern and readable flag
names.

`Use` requires a callable at construction, otherwise raises `TypeError`. Its
`validate` returns the callable result. Callable exceptions are wrapped as
`SchemaError`, while an inner `SchemaError` contributes its existing automatic
and explicit error lists.

`Const.validate` validates normally but returns the original untransformed
input. For example, `Const(Use(int)).validate("7")` returns `"7"`.

## Optional keys, defaults, and hooks

```python
Optional(key_schema, default=<omitted>)
Hook(key_schema, handler=lambda *args: None, ...)
Forbidden(key_schema, ...)
```

`Optional` makes a mapping key non-required. Equality and hashing include its
wrapped schema and whether/equal-to-what default it has. If no input key
matches an optional with a default, the result receives the default under the
string form of the key. A non-callable default is inserted verbatim and is not
validated by the mapping value schema. A callable default is invoked after
normal validation: callables with no parameters receive no arguments;
callables with parameters receive all `validate(**kwargs)`. Each validation
invokes it afresh. Defaults are accepted only for simple comparable key
schemas; a complex key such as `And(...)` raises `TypeError`.

`Hook` is an optional mapping key with a public `key` and `handler`. When both
its key and paired value schema match, call
`handler(validated_key, entire_input_mapping, schema_error_text)`; the hook
does not add the key to the returned mapping, so use a normal or optional entry
for that key too when it should be retained. A value mismatch does not call the
handler.

`Forbidden` is a Hook whose matching handler raises
`SchemaForbiddenKeyError("Forbidden key encountered: <key repr> in <mapping repr>")`.
The paired value schema matters: a forbidden key with a nonmatching value can
fall through to another key schema. Forbidden matching has priority over
ordinary and optional key schemas.

## `Literal`

```python
Literal(value, description=None, title=None)
```

Properties expose `schema`, `description`, and `title`. `str(literal)` is the
wrapped value's string form. Its repr is
`Literal("<value>", description="<description or empty>")`. Validation treats
it as its wrapped literal; JSON Schema generation also uses its title and
description as annotations.

## JSON input

`Use(json.loads)` composes normally with mapping and container schemas. JSON
objects, arrays, strings, numbers, booleans, and null become their standard
Python values before subsequent validation. Decoder failures are wrapped in
`SchemaError`; transformed results remain JSON-safe when the configured
validators/defaults are JSON-safe.

## Draft-07 JSON Schema generation

`json_schema(schema_id, use_refs=False, **kwargs)` returns a JSON-serializable
dictionary. The root always includes:

```python
{"$id": schema_id, "$schema": "http://json-schema.org/draft-07/schema#"}
```

Generation maps `str`, `int`, `float`, `bool`, `list`, and `dict` to JSON
Schema `string`, `integer`, `number`, `boolean`, `array`, and `object` types.
Unknown Python types map to `string`. `None` maps to `{"type": "null"}`;
other constants use `const`. A one-element comparable `Or` uses `const`, a
multi-element comparable `Or` uses `enum`, other `Or` branches use `anyOf`, and
representable `And` branches use `allOf`. Duplicate or unrepresentable callable
branches are omitted. A container schema emits `type: array` and an `items`
schema. `Regex` emits `type: string` and `pattern`; Python named capture syntax
is converted to an unnamed group and `/` is escaped.

A mapping emits `type: object`, `properties`, `required`, and
`additionalProperties`. Literal string keys become properties; optional keys
are omitted from `required`; defaults are included in the property's `default`.
Tuple, set, and frozenset constants/defaults become arrays, `Literal` unwraps,
ordinary JSON-safe values remain unchanged, and other objects use `str(value)`.
Forbidden hooks are omitted. `additionalProperties` is true when
`ignore_extra_keys=True` or a key schema accepts all strings/objects.

`Schema.name` becomes `title`, and schema/key `description` and `Literal.title`
become annotations. A named `Schema(..., as_reference=True)` emits
`{"$ref": "#/definitions/<name>"}` and adds its complete named schema once to
the root `definitions` mapping. Reusing it produces the same reference.
Callable defaults used during JSON Schema generation receive `**kwargs` under
the same rule as validation defaults.

# Frozen Scenario Leaves

The fixed denominator is exactly 30 JSON-safe subprocess leaves:

```text
api-surface
schema-properties
primitive-validation
callable-validation
use-and-const
and-or
regex-validation
iterable-validation
mapping-validation
mapping-errors
ignore-extra-keys
optional-keys
defaults-static
defaults-callable
defaults-invalid
forbidden-keys
custom-hook
only-one-key
literal-metadata
schema-error-code
custom-errors
callable-errors
named-errors-and-validity
json-input
json-schema-basic
json-schema-types
json-schema-combinators
json-schema-metadata-defaults
json-schema-additional-properties
json-schema-definitions
```

Every schema, predicate, converter, default, and hook callback is constructed
inside a fresh unprivileged candidate subprocess. The trusted parent never
imports candidate code and compares only bounded JSON observations. Stress,
filesystem examples, hash-derived `use_refs=True` IDs, recursive references,
custom subclass internals, and unlisted JSON Schema edge cases are outside the
scored contract.
