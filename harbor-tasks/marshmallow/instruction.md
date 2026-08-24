# marshmallow

## Project Description

Build `marshmallow`, a Python library that converts complex datatypes to and from
native Python datatypes. A *schema* declares named *fields*; the schema then
serializes objects (`dump`) and deserializes/validates input (`load`), collecting
structured validation messages instead of failing on the first problem.

The library is pure Python, has no runtime dependencies on Python 3.11+, performs
no network or filesystem access, and is deterministic.

## Supports

- Python `>=3.10`, graded on CPython 3.12.
- Distribution and import name `marshmallow`, version `4.3.1`.
- Installable from the workspace root with a PEP 517 build (`pip install .`).
  The package must be importable as `marshmallow` after installation.
- No third-party runtime dependencies on Python 3.11+. Do not declare stdlib
  modules as dependencies.
- Public modules: `marshmallow`, `marshmallow.fields`, `marshmallow.validate`.

## API Usage Guide

### `marshmallow.__all__`

The root package must export exactly these 14 names:

```text
EXCLUDE, INCLUDE, RAISE, Schema, SchemaOpts, ValidationError, fields, missing,
post_dump, post_load, pre_dump, pre_load, validates, validates_schema
```

`RAISE`, `EXCLUDE`, and `INCLUDE` are the unknown-field policy constants with the
string values `"raise"`, `"exclude"`, and `"include"`. Any place accepting an
`unknown` option accepts these strings. `missing` is a singleton sentinel marking
an absent value; it is falsy.

### `marshmallow.fields.__all__`

The fields module must export exactly these 37 names:

```text
AwareDateTime, Bool, Boolean, Constant, Date, DateTime, Decimal, Dict, Email,
Enum, Field, Float, Function, IP, IPInterface, IPv4, IPv4Interface, IPv6,
IPv6Interface, Int, Integer, List, Mapping, Method, NaiveDateTime, Nested,
Number, Pluck, Raw, Str, String, Time, TimeDelta, Tuple, URL, UUID, Url
```

`Str`, `Int`, `Bool`, and `URL` are aliases of `String`, `Integer`, `Boolean`, and
`Url`.

### `marshmallow.validate`

Provides the callable validator base `Validator` plus `And`, `ContainsNoneOf`,
`ContainsOnly`, `Email`, `Equal`, `Length`, `NoneOf`, `OneOf`, `Predicate`,
`Range`, `Regexp`, and `URL`. A validator is constructed with its constraint and
then called with a value; it raises `ValidationError` when the value violates the
constraint.

- `Range(min=None, max=None, *, min_inclusive=True, max_inclusive=True, error=None)`
- `Length(min=None, max=None, *, equal=None, error=None)`
- `OneOf(choices, labels=None, *, error=None)`
- `And(*validators, error=None)` runs validators in order and aggregates messages.

### `Schema`

```python
Schema(*, only=None, exclude=(), many=None, load_only=(), dump_only=(),
       partial=None, unknown=None)
```

Declare fields as class attributes, or build a schema class at runtime:

```python
Schema.from_dict(fields: dict[str, Field], *, name: str = "GeneratedSchema") -> type[Schema]
```

`from_dict` returns an unregistered schema class. Instance attribute `fields` is a
mapping of the schema's resolved field names to field instances, honouring `only`
and `exclude`.

Class-level configuration uses an inner `class Meta` supporting at least
`fields`, `additional`, `unknown`, `many`, `load_only`, `dump_only`, and
`render_module`. `SchemaOpts` holds the resolved options.

Methods:

- `dump(obj, *, many=None)` returns native Python data. Missing values are
  omitted unless the field declares `dump_default`.
- `dumps(obj, *, many=None, **kwargs)` renders `dump` output through
  `Meta.render_module` (default: stdlib `json`, so `dumps` returns a JSON string
  with declaration order preserved and `": "`/`", "` separators).
- `load(data, *, many=None, partial=None, unknown=None)` returns deserialized
  values and raises `ValidationError` when any field fails.
- `loads(text, *, many=None, partial=None, unknown=None, **kwargs)` decodes with
  the render module first, then loads.
- `validate(data, *, many=None, partial=None, unknown=None)` returns the messages
  dictionary (empty when valid) instead of raising for ordinary failures.

Option semantics:

- `many=True` processes a sequence; `load` errors are keyed by integer index.
- `only`/`exclude` narrow the field set; `only` preserves the given selection.
- `partial=True` skips all `required` checks; `partial=("name",)` skips the named
  fields only.
- `unknown` selects `RAISE` (default), `EXCLUDE`, or `INCLUDE`. `RAISE` produces
  the message `"Unknown field."` under the offending key; `EXCLUDE` drops it;
  `INCLUDE` passes the raw value through.

### `Field`

```python
Field(*, load_default=missing, dump_default=missing, data_key=None,
      validate=None, required=False, allow_none=None, load_only=False,
      dump_only=False, error_messages=None, metadata=None)
```

- `data_key` renames the external key; internal attribute names stay unchanged.
- `validate` accepts one callable or a list of callables.
- `required=True` and an absent key produce `"Missing data for required field."`.
- `None` input produces `"Field may not be null."` unless `allow_none=True`.
- `load_only` fields are excluded from `dump`; `dump_only` fields are ignored by
  `load`.

Field error messages that the grader relies on:

- integer/number parse failure: `"Not a valid integer."`
- `Range(min=0, max=150)` violation:
  `"Must be greater than or equal to 0 and less than or equal to 150."`
- `OneOf(["ab", "abc"])` violation: `"Must be one of: ab, abc."`

Composite and typed fields:

- `Nested(nested, **kwargs)` accepts a schema instance, schema class, registered
  name, field dict, or callable. Errors nest under the field name.
- `Pluck(nested, field_name, **kwargs)` serializes a single nested field value.
- `List(inner, **kwargs)` deserializes each item with `inner`; item errors are
  keyed by index.
- `Tuple(tuple_fields, **kwargs)` maps positional fields and returns a `tuple`.
- `Dict(keys=None, values=None, **kwargs)` (alias of `Mapping`) applies key and
  value fields.
- `DateTime`, `NaiveDateTime`, `AwareDateTime`, `Date`, `Time` load ISO-8601 text
  into `datetime`/`date`/`time` objects and dump back to ISO-8601 text.
- `TimeDelta` loads a number of seconds (by default) into `timedelta` and dumps a
  number.
- `Decimal(places=None, rounding=None, *, allow_nan=False, as_string=False)`
  loads `decimal.Decimal`; `as_string=True` dumps a string.
- `UUID` loads `uuid.UUID`; `IP`, `IPv4`, `IPv6` and the interface variants load
  `ipaddress` objects. All dump their string forms.
- `Enum(enum, *, by_value=False, **kwargs)` loads a member by name (default) and
  dumps the member name.
- `Function`, `Method`, and `Constant` derive values from callables, named schema
  methods, and a fixed value.

### `ValidationError`

```python
ValidationError(message, field_name="_schema", data=None, valid_data=None, **kwargs)
```

Attributes: `messages` (normalized to a dict of lists, nested for nested and
collection fields, keyed by index for `many`), `messages_dict`, `field_name`
(default `"_schema"` for schema-level failures), `data` (raw input), and
`valid_data` (the partially processed data that did validate). For a failing
`load`, `valid_data` retains the successfully deserialized entries and omits the
failing ones; for `many=True` it is the list of per-item partial results.

### Decorators

`pre_load`, `post_load`, `pre_dump`, `post_dump`, `validates`, and
`validates_schema` mark schema methods as hooks. `pre_load`/`post_load` accept
`pass_many` and `post_load` also `pass_original`; `validates(*field_names)`
attaches field validators; `validates_schema` accepts `pass_many`,
`pass_original`, and `skip_on_field_errors`. Hook ordering within one category is
unspecified.

## Implementation Notes

- Error aggregation is required: one `load` reports every failing field, not just
  the first. Nested and collection errors nest to arbitrary depth.
- Declared field order is preserved in `dump` output and in `fields`.
- Schema classes are registered by class name for string-based `Nested`
  resolution; `from_dict` results are not registered.
- Grading uses a bounded, deterministic slice of JSON-safe schema and
  serialization behavior. Every graded observation is produced by constructing
  schemas and fields from declarative input inside a single process, then
  comparing normalized native results, rendered `dumps` text, or
  `ValidationError` attributes. Mapping key order is normalized before
  comparison, so unknown-field message ordering is not graded.
- Do not require network access, and do not read configuration from the
  environment.

Example:

```python
from marshmallow import Schema, fields, validate, ValidationError

class PersonSchema(Schema):
    name = fields.Str(required=True)
    age = fields.Int(validate=validate.Range(min=0, max=150))

PersonSchema().load({"name": "Ada", "age": "36"})
# {'name': 'Ada', 'age': 36}

PersonSchema().validate({"age": "abc"})
# {'name': ['Missing data for required field.'], 'age': ['Not a valid integer.']}

try:
    PersonSchema().load({"name": "Ada", "age": -1})
except ValidationError as error:
    error.messages    # {'age': ['Must be greater than or equal to 0 and less than or equal to 150.']}
    error.valid_data  # {'name': 'Ada'}
```
