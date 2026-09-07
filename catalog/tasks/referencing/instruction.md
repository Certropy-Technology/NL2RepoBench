# Build `referencing`

Create a complete, installable Python project named `referencing` from an
empty workspace. It is a pure-Python library for resolving JSON references
across in-memory JSON documents. It must work without network access at
runtime and must not depend on a preinstalled copy of `referencing`.

## Project Description

Applications use the library to give JSON documents a specification-aware
identity, add them to immutable registries, and resolve absolute, relative,
fragment, JSON Pointer, and named-anchor references. The package supports the
JSON Schema drafts from draft-03 through draft 2020-12. It is a library, not a
JSON validator, HTTP client, or file loader.

# Natural Language Instruction

Build `referencing` from an empty workspace. Implement specification-aware
resources, immutable registries, JSON Pointer and anchor resolution, JSON
Schema dialect helpers, cached retrieval, and the documented exception types.
All ordinary operations are local and deterministic.

# Supports or Environment Configuration

- Support CPython 3.13 and newer on Linux.
- Provide an installable `referencing` package with the modules
  `referencing`, `referencing.jsonschema`, `referencing.retrieval`,
  `referencing.exceptions`, and `referencing.typing`.
- The distribution has runtime dependencies on `attrs>=22.2.0` and
  `rpds-py>=0.7.0`. They are already available in the task environment.
- Provide normal package metadata and a build configuration. A fixed local
  development version is acceptable; behavior must not depend on VCS metadata.
- Normal registry, resource, resolver, pointer, anchor, and retrieval
  operations are local and deterministic. Applications may supply a retrieval
  callback, but the library itself must not make network or subprocess calls.

# Project Directory Structure

```text
workspace/
├── pyproject.toml
├── README.md
├── LICENSE
└── referencing/
    ├── __init__.py
    ├── exceptions.py
    ├── _core.py
    ├── jsonschema.py
    ├── retrieval.py
    └── typing.py
```

The root package exports `Anchor`, `Registry`, `Resource`, and `Specification`;
the listed modules retain their public import paths.

# API Usage Guide

The root package exports exactly `Anchor`, `Registry`, `Resource`, and
`Specification` through `referencing.__all__`.

### `Resource`

`Resource(contents, specification)` binds deserialized JSON-compatible
contents to a `Specification`.

- `Resource.from_contents(contents, default_specification=Specification)`
  detects a known specification from the document's `$schema` value, or uses a
  supplied default. When no specification can be determined it raises
  `CannotDetermineSpecification`.
- `Resource.opaque(contents)` creates an opaque resource with no identifier,
  subresources, or anchors.
- `id()` returns the resource's specification-defined identifier with a
  trailing `#` removed, or `None`.
- `subresources()` and `anchors()` enumerate specification-defined nested
  resources and anchors.
- `pointer(pointer, resolver)` resolves a JSON Pointer. The empty pointer
  addresses the whole document. Object keys use `~1` for `/` and `~0` for `~`;
  sequence segments are integer indexes. A missing location raises
  `PointerToNowhere`.

### `Specification`

`Specification(name, id_of, subresources_of, anchors_in, maybe_in_subresource)`
describes how a family of document values participates in referencing.

- `create_resource(contents)` returns a `Resource` using that specification.
- `anchors_in(contents)` returns the anchors contained in its resource.
- `Specification.OPAQUE` is the public no-reference specification.
- `Specification.detect(contents)` determines a known specification from a
  document and raises `CannotDetermineSpecification` when it cannot.

### `Registry`

`Registry(resources=..., retrieve=...)` is an immutable mapping of URI strings
to resources. Every mutating-looking operation returns a new registry and does
not alter the old one.

- `with_resource(uri, resource)`, `with_resources(pairs)`, and
  `with_contents(pairs, **kwargs)` return registries extended with resources.
  A URI ending in `#` is equivalent to the URI without that fragment.
- `resource @ registry` and an iterable of resources `@ registry` add
  resources using their internal IDs. A resource without an ID raises
  `NoInternalID`.
- `crawl()` discovers nested resources and anchors. `contents(uri)`, item
  access, and `anchor(uri, name)` operate on crawled state as needed.
- `remove(uri)` returns a registry without that resource and raises
  `NoSuchResource` when it is absent.
- `combine(*registries)` unions registries. Combining distinct non-default
  retrieval callbacks raises `ValueError`.
- `get_or_retrieve(uri)` first checks known and crawled resources, then calls
  the configured callback. It returns `Retrieved(registry, value)`.
  `NoSuchResource` and `CannotDetermineSpecification` propagate; other
  callback failures become `Unretrievable`.
- `resolver(base_uri="")` and `resolver_with_root(resource)` return
  `Resolver` objects.

### `Resolver`, Anchors, and Results

`Resolver.lookup(ref)` resolves a reference relative to its base URI and
returns `Resolved(contents, resolver)`.

- A fragment beginning with `/` is a JSON Pointer; a nonempty plain fragment
  is a named anchor; an empty fragment selects the full resource.
- Missing resources and failed retrievals become `Unresolvable`. Missing named
  anchors raise `NoSuchAnchor`. An anchor text containing `/` without an
  initial pointer slash raises `InvalidAnchor`.
- `in_subresource(resource)` updates the base URI if the resource has an ID.
- `dynamic_scope()` yields prior base URIs paired with their registry.
- `Anchor(name, resource).resolve(resolver)` returns a `Resolved` value for its
  resource.

`Retrieved(registry, value)` and `Resolved(contents, resolver)` are immutable
records. Their attributes are public and preserve the associated registry or
resolver for subsequent operations.

### JSON Schema Helpers

`referencing.jsonschema.specification_with(dialect_id, default=_UNSET)` returns
the specification for these identifiers, treating a trailing `#` as
equivalent:

```text
https://json-schema.org/draft/2020-12/schema
https://json-schema.org/draft/2019-09/schema
http://json-schema.org/draft-07/schema
http://json-schema.org/draft-06/schema
http://json-schema.org/draft-04/schema
http://json-schema.org/draft-03/schema
```

An unknown dialect raises `UnknownDialect` unless a `default` is supplied, in
which case that exact default value is returned. JSON Schema resources use the
applicable `$id` or legacy `id` keyword, discover schema-valued nested
subresources, and recognize `$anchor` where that draft supports it.

`DynamicAnchor(name, resource).resolve(resolver)` follows the resolver's
dynamic scope and uses the nearest matching dynamic anchor. The
`lookup_recursive_ref(resolver)` helper implements the draft 2019 recursive
reference rule for `#`.

### Retrieval Helper

`referencing.retrieval.to_cached_resource(cache=None, loads=json.loads,
from_contents=Resource.from_contents)` decorates a simple URI-to-serialized
document callable. The returned callable loads the document, creates a
resource, and caches repeated URI requests. With no `cache` argument it uses
an unbounded in-memory cache. Custom `loads`, `from_contents`, and cache
decorators are supported.

### Exceptions

The following exception classes are public from `referencing.exceptions`:

`NoSuchResource`, `NoInternalID`, `Unretrievable`,
`CannotDetermineSpecification`, `Unresolvable`, `PointerToNowhere`,
`NoSuchAnchor`, and `InvalidAnchor`.

They preserve their public constructor fields and compare/hash by concrete
exception type and those fields. `PointerToNowhere`, `NoSuchAnchor`, and
`InvalidAnchor` provide useful string forms that identify the failed reference
or anchor.

## Determinism and Boundaries

URI insertion, reference lookup, anchor lookup, and JSON Pointer behavior must
be deterministic for the same inputs. Do not use network requests, filesystem
lookups, subprocesses, time, or random values to implement library behavior.
The retrieval callback is application-supplied and may represent remote data,
but the library must only invoke it on a missing URI and must cache or wrap its
outcome according to the API above.

The deterministic verification scope covers root exports, package installation,
specification detection, resource IDs, opaque resources, immutable registry
updates, resource crawling, exact and relative lookup, JSON Pointers and
escaping, named anchors, error types, subresource bases, registry combining and
removal, retrieval wrapping, cached retrieval, dialect selection, exception
identity, dynamic anchors, and recursive references.

# Implementation Notes

Registry updates are persistent and must not mutate an earlier registry.
Reference resolution preserves base URIs, fragment distinctions, JSON Pointer
escaping, named-anchor behavior, and specification-defined discovery. Retrieval
callbacks run only for missing URIs and failures map to the documented errors.

# Examples

```python
from referencing import Registry, Resource
resource = Resource.opaque({"answer": 42})
registry = Registry().with_resource("urn:example", resource)
```

```python
registry.contents("urn:example")
```

```python
registry.resolver("urn:example").lookup("#")
```

# Error Handling and Boundary Conditions

Unknown specifications raise `CannotDetermineSpecification`; missing resources
raise `NoSuchResource` or `Unresolvable`; missing anchors raise `NoSuchAnchor`;
bad pointers raise `PointerToNowhere`. Do not perform filesystem or network
lookups implicitly.
