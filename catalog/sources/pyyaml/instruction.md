# Build `PyYAML`

Create a complete, installable Python project named `PyYAML` from an empty
workspace. The distribution must provide the `yaml` package and implement the
behavior of the frozen PyYAML revision described below. Do not depend on a
preinstalled copy of PyYAML or on network access during evaluation.

## Project Description

PyYAML is a YAML 1.1 parser and emitter for Python. It converts YAML streams to
ordinary Python values, emits Python values as YAML, and exposes lower-level
scanner, parser, composer, constructor, resolver, representer, event, token,
and node APIs. The package also supports application-defined constructors and
representers.

## Supports

- Support CPython 3.10 and newer Python 3.x versions in the supported source
  range. The evaluated environment is CPython 3.12 on Debian 12.
- Provide an installable project with `yaml/__init__.py` and the public modules
  used by the APIs below. `pip install .` must work from the workspace root.
- Declare no third-party runtime dependency. The optional LibYAML C extension
  is not required for this task; the pure-Python implementation is the
  deterministic baseline and must expose `__with_libyaml__` as false when the
  extension is unavailable.
- Keep normal parsing, dumping, event, node, and registration operations local:
  no network, subprocess, external service, or current-time behavior is allowed.

## API Usage Guide

### Root package functions

Import path: `import yaml`

- `yaml.safe_load(stream)` and `yaml.full_load(stream)` return one Python value
  from the first YAML document. `safe_load` resolves only basic YAML tags;
  `full_load` additionally resolves the non-unsafe standard Python-facing tags.
  Empty input returns `None`.
- `yaml.safe_load_all(stream)` and `yaml.full_load_all(stream)` return a lazy
  iterator over all documents in stream order. Multiple documents are separated
  by `---`.
- `yaml.load(stream, Loader)` and `yaml.load_all(stream, Loader)` require
  an explicit loader argument. Omitting it raises `TypeError`.
- `yaml.dump(data, stream=None, Dumper=yaml.Dumper, default_style=None,
  default_flow_style=False, canonical=None, indent=None, width=None,
  allow_unicode=None, line_break=None, encoding=None, explicit_start=None,
  explicit_end=None, version=None, tags=None, sort_keys=True)` returns a text
  string when `stream` is `None`, or writes the same representation to a text or
  binary stream and returns `None`. Mappings are sorted by key by default;
  `sort_keys=False` preserves insertion order.
- `yaml.safe_dump` and `yaml.safe_dump_all` use the safe representer and reject
  unsupported arbitrary Python objects with `yaml.representer.RepresenterError`.
- `yaml.parse(stream, Loader=yaml.Loader)` yields event objects in stream order;
  `yaml.scan(stream, Loader=yaml.Loader)` yields token objects. `compose` and
  `compose_all` return representation `Node` objects. These iterators are lazy
  and must preserve document boundaries.
- `yaml.emit(events, stream=None, Dumper=yaml.Dumper, ...)` emits events to text
  and returns the generated string when no stream is supplied. `serialize` and
  `serialize_all` emit nodes, while `dump` and `dump_all` represent Python
  values.
- `yaml.add_implicit_resolver(tag, regexp, first=None, Loader=None,
  Dumper=yaml.Dumper)`, `yaml.add_path_resolver(tag, path, kind=None,
  Loader=None, Dumper=yaml.Dumper)`, `yaml.add_constructor(tag, constructor,
  Loader=None)`, `yaml.add_multi_constructor(tag_prefix, multi_constructor,
  Loader=None)`, `yaml.add_representer(data_type, representer,
  Dumper=yaml.Dumper)`, and `yaml.add_multi_representer(data_type,
  multi_representer, Dumper=yaml.Dumper)` register behavior on the selected
  loader or dumper class. A registration affects later operations in that
  process and preserves the normal class-level lookup rules.

### Loaders, dumpers, events, tokens, and nodes

The public classes include `BaseLoader`, `SafeLoader`, `FullLoader`, `Loader`,
`UnsafeLoader`, and their `C*` counterparts when the optional extension exists;
`BaseDumper`, `SafeDumper`, and `Dumper`; event classes such as
`StreamStartEvent`, `DocumentStartEvent`, `ScalarEvent`, `SequenceStartEvent`,
`MappingStartEvent`, and their corresponding end classes; token classes such as
`ScalarToken`, `KeyToken`, `ValueToken`, and flow/block delimiters; and node
classes `ScalarNode`, `SequenceNode`, and `MappingNode`.

Event and token constructors retain their declared attributes, including
anchors, tags, implicit flags, values, marks, and document metadata. A composed
scalar node has its resolved tag and scalar value; sequence and mapping nodes
retain child order. `yaml.parse`, `yaml.scan`, and `yaml.compose` raise a
subclass of `yaml.YAMLError` for malformed YAML.

### Custom types and errors

`yaml.YAMLObject` and `yaml.YAMLObjectMetaclass` support classes declaring
`yaml_loader`, `yaml_dumper`, and `yaml_tag`, with `from_yaml` and `to_yaml`
hooks used for construction and representation. Custom constructors and
representers may be registered with the class methods on a loader or dumper.

The error module exposes `Mark`, `YAMLError`, and `MarkedYAMLError`; parser,
scanner, composer, constructor, reader, emitter, serializer, and representer
failures are represented by the corresponding `*Error` subclasses. Invalid
input must raise these typed exceptions rather than being silently accepted.

## Implementation Notes

- Use a `lib/` source layout or another layout that installs the `yaml` package
  and all required public submodules. The installed distribution metadata must
  identify itself as `PyYAML` and expose a version string.
- Preserve Python object types for booleans, integers, floats, nulls, strings,
  byte strings, lists, tuples, mappings, sets, timestamps, and aliases where
  the selected loader defines them. Anchors and aliases must preserve shared
  object identity when constructing values.
- YAML merge keys (`<<`) must merge mappings in the documented precedence order
  and deduplicate repeated aliases without losing explicitly written keys.
- Safe loading must not construct arbitrary Python objects from untrusted tags.
  `safe_dump` must not serialize unsupported application objects by guessing.
- Determinism matters: equivalent calls with the same input and options produce
  the same values, event/token sequences, and emitted bytes. Do not copy hidden
  tests or write verifier-owned reports from the candidate project.
