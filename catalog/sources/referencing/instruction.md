# Build `referencing`

## Project Description

Create an installable Python implementation of `referencing`, a small, immutable
JSON-reference registry and resolver library. The package models documents as
resources interpreted by a specification, stores and lazily crawls resources in
registries, resolves URI references, anchors, and JSON Pointers, and includes
the historic and current JSON Schema referencing specifications.

The implementation starts from an empty workspace. It must reproduce the public
behavior described below without retrieving the upstream project or any other
source implementation.

## Supports

- Python 3.13 or newer.
- An installable project named `referencing` with a standard `pyproject.toml`.
- Runtime dependencies `attrs>=22.2.0` and `rpds-py>=0.7.0` may be used; they are
  already available in the execution image.
- Public modules: `referencing`, `referencing.exceptions`,
  `referencing.jsonschema`, `referencing.retrieval`, and `referencing.typing`.
- Objects representing resources, specifications, registries, resolvers,
  anchors, retrieved values, and resolved values are immutable value objects.
  Equal instances compare by value and are hashable when their fields are
  hashable.
- Registry operations are persistent: methods that add, remove, combine, crawl,
  or retrieve resources return a new registry and do not mutate the original.
- URI handling uses RFC 3986 joining and fragment removal. Registry keys and
  resource identifiers with an empty trailing `#` are normalized to the same
  fragmentless URI.
- No operation performs network I/O by itself. Dynamic retrieval only invokes
  the caller-supplied retrieval callable.

## API Usage Guide

### Top-level exports

`referencing.__all__` is exactly:

```python
["Anchor", "Registry", "Resource", "Specification"]
```

The corresponding classes are importable directly from `referencing`.

### `Specification`

```python
Specification(
    name: str,
    id_of: Callable[[D], str | None],
    subresources_of: Callable[[D], Iterable[D]],
    anchors_in: Callable[[Specification[D], D], Iterable[Anchor[D]]],
    maybe_in_subresource: Callable[..., Resolver[D]],
)
```

- `repr(specification)` is `<Specification name='NAME'>`.
- `anchors_in(contents)` delegates to the configured anchor callback.
- `create_resource(contents)` returns a `Resource` using that specification.
- `Specification.OPAQUE` is named `opaque`; it reports no identifier,
  subresources, or anchors and never changes a resolver while traversing.
- `Specification.detect(contents)` attempts dialect detection and raises
  `CannotDetermineSpecification(contents=contents)` when no dialect is
  discernible. Calling `specific_spec.detect(contents)` uses that instance as
  the default only when the contents do not identify a dialect; an explicit
  recognized dialect always wins, and an explicit unknown or non-string
  dialect does not silently use the default.

### `Resource`

```python
Resource(contents: D, specification: Specification[D])
Resource.from_contents(
    contents: D,
    default_specification: type[Specification[D]] | Specification[D] = Specification,
) -> Resource[D]
Resource.opaque(contents: D) -> Resource[D]
```

- `from_contents` detects the specification as described above.
- `opaque` creates a resource using `Specification.OPAQUE`.
- `id() -> str | None` calls the specification's identifier function and strips
  all trailing empty-fragment `#` characters from a non-`None` identifier.
- `subresources() -> Iterable[Resource[D]]` wraps every immediate subdocument
  reported by the specification, using the current specification as the
  default when the subdocument has no explicit dialect.
- `anchors() -> Iterable[Anchor]` returns the specification-defined anchors.
- `pointer(pointer: str, resolver: Resolver[D]) -> Resolved[D]` resolves a JSON
  Pointer. An empty pointer returns the whole document. Object segments decode
  `%xx`, then `~1` to `/` and `~0` to `~`; sequence segments are decimal integer
  indexes. Missing keys or indexes raise `PointerToNowhere` with the original
  pointer and resource, chained from the underlying lookup error. Traversal
  enters specification-defined subresources so subsequent relative references
  use the correct base URI.

### `Registry`

```python
Registry(
    resources: Mapping[str, Resource[D]] = {},
    anchors = {},
    uncrawled = {},
    retrieve: Callable[[str], Resource[D]] = default_failure,
)
```

`Registry` implements `collections.abc.Mapping[str, Resource[D]]`:

- `registry[uri]` strips trailing empty fragments and returns an already known
  resource, or raises `NoSuchResource(ref=uri)` instead of exposing `KeyError`.
- Iteration yields known URIs and `len(registry)` counts known resources.
- `contents(uri)` returns `registry[uri].contents` with the same exception
  contract.
- `with_resource(uri, resource)` and `with_resources(pairs)` add resources
  without crawling them. Input URIs are normalized by removing trailing `#`.
- `with_contents(pairs, **kwargs)` converts contents through
  `Resource.from_contents`, forwarding keyword arguments such as
  `default_specification`.
- `resource @ registry` and `iterable_of_resources @ registry` add resources
  under their internal IDs. A resource without an ID raises
  `NoInternalID(resource=resource)`.
- `remove(uri)` removes the resource, its uncrawled marker, and its known
  anchors. A missing URI raises `NoSuchResource`.
- `combine(*registries)` merges resources, anchors, and uncrawled state. The
  same registry combined only with itself is returned unchanged. At most one
  distinct non-default retrieval function may be present; conflicting
  retrieval functions raise `ValueError` with a message explaining the
  conflict.
- `crawl()` recursively discovers immediate subresources and anchors. A
  subresource ID is joined against the URI of its containing resource. Crawling
  is lazy and leaves the original registry unchanged.
- `get_or_retrieve(uri) -> Retrieved` checks current resources, then a crawled
  registry, then calls `retrieve(uri)`. A newly retrieved resource is added
  under the requested URI in the returned registry. `NoSuchResource` and
  `CannotDetermineSpecification` from the callback propagate unchanged; any
  other callback exception is wrapped as `Unretrievable(ref=uri)` with the
  callback error as its cause.
- `anchor(uri, name) -> Retrieved` lazily crawls and finds an anchor first under
  the requested URI and then under the resource's canonical ID. Missing
  resources raise `NoSuchResource`; names containing `/` that are not found
  raise `InvalidAnchor`; other missing names raise `NoSuchAnchor`.
- `resolver(base_uri: str = "")` and `resolver_with_root(resource)` create
  resolvers backed by the registry. The latter adds the root under its ID or
  the empty URI.
- `repr(registry)` reports its resource count and whether all or some resources
  remain uncrawled, using singular `resource` only for a count of one.

### Retrieved and resolved values

`Retrieved(value, registry)` and `Resolved(contents, resolver)` are immutable
value objects. `Retrieved.registry` is the updated registry that made a lookup
possible. `Resolved.resolver` is the resolver to use for subsequent relative
resolution.

### `Resolver` and `Anchor`

Resolvers are obtained from registry methods; direct construction is not a
supported user workflow.

```python
resolver.lookup(ref: str) -> Resolved[D]
resolver.in_subresource(subresource: Resource[D]) -> Resolver[D]
resolver.dynamic_scope() -> Iterable[tuple[str, Registry[D]]]
Anchor(name: str, resource: Resource[D])
anchor.resolve(resolver: Resolver[D]) -> Resolved[D]
```

- `lookup` resolves non-fragment references with `urljoin(base_uri, ref)`, then
  removes the fragment. A `#`-relative reference uses the current base URI.
- An empty fragment returns the resource contents. A fragment beginning `/` is
  a JSON Pointer. Any other nonempty fragment is a plain anchor name.
- A missing or unretrievable resource raises `Unresolvable(ref=the_original_ref)`;
  an `Unretrievable` is retained as the cause. Anchor and pointer exceptions
  propagate as their specific subclasses.
- Resolution returns a resolver updated with the registry produced by crawling
  or retrieval and with the resolved resource URI as its base.
- `in_subresource` returns the same resolver when the subresource has no ID;
  otherwise it joins the subresource ID to the current base URI.
- `dynamic_scope` yields prior nonempty base URIs from newest to oldest, paired
  with the current registry.
- A plain `Anchor.resolve` returns its resource contents and the supplied
  resolver unchanged.

### JSON Schema specifications

`referencing.jsonschema` exports the aliases `ObjectSchema`, `Schema`,
`SchemaResource`, and `SchemaRegistry`, plus:

```python
EMPTY_REGISTRY: SchemaRegistry
DRAFT202012: Specification  # name "draft2020-12"
DRAFT201909: Specification  # name "draft2019-09"
DRAFT7: Specification       # name "draft-07"
DRAFT6: Specification       # name "draft-06"
DRAFT4: Specification       # name "draft-04"
DRAFT3: Specification       # name "draft-03"
specification_with(dialect_id: str, default=...) -> Specification
DynamicAnchor(name: str, resource: SchemaResource)
lookup_recursive_ref(resolver: Resolver[Schema]) -> Resolved[Schema]
```

- `EMPTY_REGISTRY` equals an empty `Registry`.
- `specification_with` recognizes the six official dialect URI values with or
  without an empty trailing `#`. Unknown dialects return an explicitly supplied
  default; without one they raise `UnknownDialect(uri=dialect_id)`.
- Modern drafts use `$id`; drafts 7 and 6 ignore `$id` when `$ref` is present
  and do not treat fragment-only `$id` values as resource IDs. Drafts 4 and 3
  apply the same rules to `id`.
- Draft 2020-12 discovers immediate subschemas in singular schema keywords,
  arrays such as `allOf`/`anyOf`/`oneOf`/`prefixItems`, and mapping values such
  as `$defs`, `properties`, `patternProperties`, and `dependentSchemas`.
  Draft 2019-09 uses its corresponding vocabulary. Older drafts additionally
  support tuple-valued `items`, schema-valued `dependencies`, and the legacy
  keyword sets defined by those drafts. Non-schema keywords are not crawled.
- Draft 2020-12 creates plain anchors from `$anchor` and dynamic anchors from
  `$dynamicAnchor`; draft 2019-09 supports `$anchor`; older drafts use a
  fragment-only identifier as a plain anchor.
- `DynamicAnchor.resolve` searches dynamic scope for later dynamic anchors of
  the same name and resolves to the last matching resource, entering that
  subresource. `lookup_recursive_ref` implements the draft 2019-09 recursive
  `#` lookup across dynamic scope.

### Exceptions

`referencing.exceptions` exports these value-based, hashable exception types:

```python
NoSuchResource(ref: str)                 # also a KeyError
NoInternalID(resource: Resource)
Unretrievable(ref: str)                  # also a KeyError
CannotDetermineSpecification(contents)
Unresolvable(ref: str)
PointerToNowhere(ref: str, resource: Resource)
NoSuchAnchor(ref: str, resource: Resource, anchor: str)
InvalidAnchor(ref: str, resource: Resource, anchor: str)
```

Equality requires the same concrete exception class and equal fields.
`PointerToNowhere`, `NoSuchAnchor`, and `InvalidAnchor` provide descriptive
strings naming the missing pointer or anchor and the resource contents. The
special pointer `/` message explains that it names the empty-string property,
whereas `#` names the whole resource.

`referencing.jsonschema.UnknownDialect(uri: str)` is an immutable exception
whose `uri` field contains the unrecognized dialect.

### Retrieval helper

```python
referencing.retrieval.to_cached_resource(
    cache: Callable | None = None,
    loads: Callable = json.loads,
    from_contents: Callable = Resource.from_contents,
) -> Callable
```

This decorator converts a simple `uri -> serialized value` callable into a
registry retrieval callable. It loads the returned value, converts the decoded
contents to a resource, and caches by URI. With `cache=None`, use an unbounded
`functools.lru_cache`. Custom cache decorators, loaders, and resource factories
are called exactly in that order and their return values are preserved.

### Typing helpers

`referencing.typing.URI` is an alias of `str`. `Retrieve[D]` is a protocol for
`(uri: URI) -> Resource[D]`. `Anchor[D]` is a protocol exposing a string `name`
property and `resolve(resolver) -> Resolved[D]`.

## Implementation Notes

- JSON documents may be dictionaries, lists, scalars, or booleans where the
  active specification permits them. Do not assume every schema is a mapping.
- Preserve resource insertion and resolver state immutably. Callers may retain
  and reuse every earlier registry or resolver value.
- Crawling and subresource iteration need not promise a particular order;
  behavior and membership must be deterministic for the same inputs.
- Candidate installation and verification run without network access. The
  verifier uses isolated subprocesses and fixed JSON requests; no CLI is
  required.
