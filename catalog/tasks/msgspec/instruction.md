# Build `msgspec`

Create an installable Python package named `msgspec` from an empty workspace. It is a fast, typed serialization and validation library. The implementation must be self-contained in a normal Python package and must build successfully with `pip install .` and editable installation on CPython 3.12. The package may use a C extension for speed, but correctness must not depend on network access at runtime.

## Project Description

Implement the public core of `msgspec` as a deterministic library for defining typed records (`Struct`), converting records to and from builtin values, and encoding or decoding JSON and MessagePack. Include the optional TOML and YAML modules. The package must expose the documented names from `msgspec` and its submodules; it must not require a running service, filesystem state, environment variables, or network access for library operations.

## Supports

- Provide an installable package with `msgspec/__init__.py`, `msgspec/json.py`, `msgspec/msgpack.py`, `msgspec/structs.py`, `msgspec/inspect.py`, `msgspec/toml.py`, `msgspec/yaml.py`, and `msgspec/py.typed` as appropriate.
- Target CPython 3.12 on Linux amd64. Declare the package name `msgspec` and a valid package version. Build metadata must use a standard setuptools backend; do not fetch anything while the library is imported or used.
- Runtime library code may use only the standard library. TOML encoding may depend on `tomli-w`, and YAML encoding/decoding may depend on `PyYAML`; declare optional dependencies or provide the documented missing-dependency error.
- Preserve insertion order in ordinary mappings and Struct fields. Operations that promise deterministic or sorted ordering must produce the same bytes on repeated calls.
- Exceptions must be specific and must not silently turn malformed input, missing required fields, unknown fields in strict typed decoding, or unsupported values into successful results.

## API Usage Guide

### `msgspec.Struct` and `msgspec.StructMeta`

Import path: `msgspec.Struct` and `msgspec.StructMeta`.

Define records by subclassing `Struct`, with annotated fields and optional defaults:

```python
class User(msgspec.Struct, rename="camel", omit_defaults=True):
    user_id: int
    name: str
    active: bool = True
```

The generated constructor accepts positional fields in declaration order and keyword fields by Python name. Missing required fields and unexpected keyword fields raise `TypeError`. Instances expose fields as attributes, have a deterministic class-based representation, compare by value when `eq=True`, and support pattern matching through `__match_args__`.

Support these class options: `tag`, `tag_field`, `rename` (`lower`, `upper`, `camel`, `pascal`, `kebab`, a mapping, or a callable), `omit_defaults`, `forbid_unknown_fields`, `frozen`, `eq`, `order`, `kw_only`, `repr_omit_defaults`, `array_like`, `gc`, `weakref`, `dict`, and `cache_hash`. Options must be reflected by encoding, construction, comparison, mutation, and representation where applicable. `StructMeta` must be usable as a metaclass.

### `msgspec.field`

Signature: `field(*, default=NODEFAULT, default_factory=NODEFAULT, name=None) -> Any`.

Use it in a Struct definition to specify a default, a zero-argument default factory, or the encoded field name. Reject incompatible combinations. A default factory runs once per instance and must not share mutable state.

### `msgspec.defstruct`

Signature: `defstruct(name, fields, *, bases=None, module=None, namespace=None, tag=None, tag_field=None, rename=None, omit_defaults=False, forbid_unknown_fields=False, frozen=False, eq=True, order=False, kw_only=False, repr_omit_defaults=False, array_like=False, gc=True, weakref=False, dict=False, cache_hash=False) -> type[Struct]`.

Create a Struct class dynamically. `fields` accepts names or `(name, type)` / `(name, type, default)` tuples. The result must be constructible, expose the requested field metadata, and work with the JSON and MessagePack typed codecs.

### Builtin conversion helpers

`msgspec.to_builtins(obj, *, str_keys=False, builtin_types=None, enc_hook=None, order=None) -> Any` converts Structs, dataclasses, enums, dates, mappings, sequences, and supported scalar values to JSON/MessagePack-compatible builtin values. `order` may be `"deterministic"` or `"sorted"`; unsupported values either pass through via `enc_hook` or raise `TypeError`.

`msgspec.convert(obj, type, *, strict=True, from_attributes=False, dec_hook=None, builtin_types=None, str_keys=False) -> object` validates and converts builtin data into the requested type, including nested Structs, lists, tuples, dictionaries, unions, enums, and optional values. In strict mode do not coerce incompatible scalar types. `from_attributes=True` may read named attributes from an object.

### `msgspec.structs`

- `replace(struct, /, **changes) -> Struct`: return a new instance with named fields replaced; leave the original unchanged.
- `asdict(struct, /) -> dict`: return field-name keyed builtin data using Python field names.
- `astuple(struct, /) -> tuple`: return field values in declaration order.
- `force_setattr(struct, name, value) -> None`: set a field even on a frozen Struct when the operation is permitted by the type.
- `fields(type_or_instance) -> tuple[FieldInfo, ...]`: return ordered metadata. Each `FieldInfo` has `name`, `encode_name`, `type`, `default`, `default_factory`, and a boolean `required` property.

### `msgspec.json`

- `encode(obj, /, *, enc_hook=None, order=None) -> bytes`: encode supported values as UTF-8 JSON. Mapping order is preserved unless `order="deterministic"` or `order="sorted"` is requested. `enc_hook` handles unsupported values.
- `decode(buf, /, *, type=..., strict=True, dec_hook=None) -> object`: accept `str`, `bytes`, `bytearray`, or `memoryview`; decode JSON and optionally validate into `type`. Reject trailing data and malformed UTF-8/JSON.
- `Encoder(*, enc_hook=None, decimal_format="string", uuid_format="canonical", order=None)`: reusable encoder with `encode`, `encode_lines`, and `encode_into(obj, buffer, offset=0)` methods.
- `Decoder(type=..., *, strict=True, dec_hook=None, float_hook=None)`: reusable decoder with `decode` and `decode_lines` methods.
- `format(buf, /, *, indent=2) -> str | bytes`: parse and pretty-format valid JSON while retaining the input kind.
- `schema(type, *, schema_hook=None, ref_template="#/$defs/{name}") -> dict` and `schema_components(types, *, schema_hook=None, ref_template="#/$defs/{name}") -> tuple`: produce deterministic JSON Schema descriptions for supported type annotations and Structs.

### `msgspec.msgpack`

- `encode(obj, /, *, enc_hook=None, order=None) -> bytes` and `decode(buf, /, *, type=..., strict=True, dec_hook=None, ext_hook=None) -> object` provide MessagePack serialization with the same typed Struct semantics.
- `Encoder(*, enc_hook=None, decimal_format="string", uuid_format="canonical", order=None)` provides `encode` and `encode_into`.
- `Decoder(type=..., *, strict=True, dec_hook=None, ext_hook=None)` provides typed `decode`.
- `Ext(code, data)` represents an extension value. Preserve its integer code and byte payload; `ext_hook(code, data)` may map it during decoding.

### `msgspec.toml` and `msgspec.yaml`

`encode(obj, /, *, enc_hook=None, order=None) -> bytes` and `decode(buf, /, *, type=..., strict=True, dec_hook=None) -> object` use TOML and YAML respectively, accept text or buffer inputs as documented, preserve typed Struct behavior, and raise a clear `ImportError` if the optional backend is unavailable.

### `msgspec.Meta` and inspect helpers

`Meta` stores validation/schema metadata such as `gt`, `ge`, `lt`, `le`, `multiple_of`, `pattern`, `min_length`, `max_length`, `tz`, `title`, `description`, `examples`, `extra_json_schema`, and `extra`. `msgspec.inspect.type_info(type)` and `multi_type_info(types)` return stable type-description objects; implement the common scalar, collection, union, and Struct cases needed by schema generation.

## Implementation Notes

- Keep public imports and re-exports consistent: `Struct`, `StructMeta`, `field`, `defstruct`, `Raw`, `Meta`, `UNSET`, `UnsetType`, `NODEFAULT`, `convert`, `to_builtins`, the four exception classes, and the `json`, `msgpack`, `structs`, `inspect`, `toml`, and `yaml` modules.
- Do not expose hidden tests, reference source, or verifier-specific files in the package. Do not solve the task by depending on an already-installed `msgspec` package; the candidate must install from the workspace it creates.
- Keep error paths deterministic and ensure callbacks/hooks are called only for values they are responsible for. Do not mutate caller-owned input buffers or mappings unexpectedly.
- The evaluator exercises the behavior through an isolated subprocess and JSON-safe scenarios, including nested typed Structs, rename/default options, deterministic encoding, reusable encoder/decoder methods, extension values, schema output, optional formats, malformed input, and frozen/error boundaries.
