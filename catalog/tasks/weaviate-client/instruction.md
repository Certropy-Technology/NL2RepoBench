# Project Description

Implement a clean-room Python package that reproduces the focused offline
contract of `weaviate-client` version `4.23.1.dev26+g9f59a367f`. The package is
the client-side SDK for Weaviate. This task covers deterministic behavior that
does not require a running database: authentication value objects, connection
parameters, utility conversion, filter and query builders, collection schema
configuration, and HFresh vector-index updates.

The implementation must install from an empty repository and provide the
`weaviate` import tree. Constructing and using the APIs described below must not
open sockets, resolve public hosts, download an embedded server, or contact a
Weaviate instance.

# Supports

- Python 3.12 on Linux amd64.
- Installation with `pip install --no-deps --no-build-isolation .`.
- Distribution name `weaviate-client`, version
  `4.23.1.dev26+g9f59a367f`, `Requires-Python: >=3.10`, and BSD-3-Clause
  licensing.
- Runtime requirements declared with these compatible ranges:
  `httpx>=0.26.0,<0.29.0`, `validators>=0.34.0,<1.0.0`,
  `authlib>=1.6.7,<2.0.0`, `pydantic>=2.12.0,<3.0.0`,
  `grpcio>=1.59.5,<1.80.0`, `protobuf>=4.21.6,<7.0.0`, and
  `packaging>=21.0`. The optional `agents` extra declares
  `weaviate-agents>=1.0.0,<2.0.0` but is not required at runtime.
- Root exports for `WeaviateClient`, `WeaviateAsyncClient`,
  `connect_to_local`, `connect_to_custom`, `use_async_with_local`, and the
  `auth`, `classes`, `collections`, and `exceptions` namespaces.
- `weaviate.classes` namespace modules named `init`, `query`, and `config`.

The environment already contains the exact compatible dependency closure.
Do not implement or vendor replacements for Pydantic, HTTPX, gRPC, Protobuf,
Authlib, or validators.

# API Usage Guide

## Authentication

Under both `weaviate.auth` and `weaviate.classes.init`, provide `Auth` with:

```python
Auth.api_key(api_key: str)
Auth.client_credentials(client_secret: str, scope: str | list[str] | None = None)
Auth.client_password(username: str, password: str, scope: str | list[str] | None = None)
Auth.bearer_token(access_token: str, expires_in: int = 60, refresh_token: str | None = None)
```

Return dataclass-like immutable-value objects with the supplied fields.
Credential scopes supplied as a space-separated string become `scope_list`
entries split on spaces; a list is preserved and `None` produces an empty
list. A negative bearer-token lifetime is accepted but emits one `UserWarning`
whose message begins `Auth003:`. Keep the compatibility aliases
`AuthApiKey`, `AuthBearerToken`, `AuthClientCredentials`, and
`AuthClientPassword`.

## Connection configuration

In `weaviate.config`, implement:

```python
Timeout(query: int | float = 30, insert: int | float = 90,
        init: int | float = 2, stream: int | float | None = None)
Proxies(http: str | None = None, https: str | None = None,
        grpc: str | None = None)
AdditionalConfig(connection=ConnectionConfig(), proxies: str | Proxies | None = None,
                 timeout: tuple[int, int] | Timeout = Timeout(),
                 trust_env: bool = False, grpc_config: GrpcConfig | None = None)
```

Timeout fields are non-negative Pydantic fields. `AdditionalConfig.timeout`
always returns a `Timeout`; a two-item tuple maps to query and insert while
retaining the other defaults. A string proxy applies to HTTP, HTTPS, and gRPC;
a `Proxies` model omits unset values. Explicit proxies take precedence over
environment proxy variables.

In `weaviate.connect.base`, implement:

```python
ProtocolParams(host: str, port: int, secure: bool)
ConnectionParams.from_url(url: str, grpc_port: int,
                          grpc_secure: bool = False) -> ConnectionParams
ConnectionParams.from_params(http_host: str, http_port: int, http_secure: bool,
                             grpc_host: str, grpc_port: int,
                             grpc_secure: bool) -> ConnectionParams
```

Hosts cannot be empty and ports are in `[0, 65535]`. `from_url` accepts only
HTTP and HTTPS, supplies default ports 80 or 443, and makes gRPC secure when
either `grpc_secure` is true or the URL is HTTPS. HTTP and gRPC cannot share
the same host and port. Preserve `_http_url`, `_grpc_target`, `is_gcp()`, and
`is_gcp_on_wcd()` behavior used by the client helpers.

## Utility functions

Implement these functions in `weaviate.util` with the shown signatures and
deterministic return/exception behavior:

```python
get_valid_uuid(value: str | uuid.UUID) -> str
is_weaviate_object_url(url: str) -> bool
is_object_url(url: str) -> bool
generate_uuid5(identifier: object, namespace: object = "") -> str
get_vector(vector: Sequence) -> Sequence[float]
get_domain_from_weaviate_url(url: str) -> str
parse_version_string(ver_str: str) -> tuple[int, int]
is_weaviate_domain(url: str) -> bool
```

`get_valid_uuid` accepts canonical UUIDs, compact UUIDs, UUID objects,
`weaviate://host/[Class/]uuid` beacons, and `/v1/objects/uuid` URLs. It returns
the canonical lowercase hyphenated spelling. Invalid values raise `TypeError`
for the wrong input type or `ValueError` for malformed content.
`is_weaviate_object_url` validates the scheme, localhost or a valid domain,
an optional class segment, and UUID. `is_object_url` recognizes only the
`/v1/objects/uuid` path form.

`generate_uuid5` uses `uuid.NAMESPACE_DNS` over the concatenated string forms
of namespace and identifier. `get_vector` returns lists unchanged and accepts
objects exposing NumPy/Tensor-style `squeeze().tolist()`, TensorFlow-style
`numpy().squeeze().tolist()`, or Series-style `to_list()`; unsupported values
raise `TypeError`. `parse_version_string` accepts an optional `v`, ignores
patch components, and defaults a missing minor component to zero.

Also preserve the local conversion contracts for `_sanitize_str`,
`_to_beacons`, `_get_valid_timeout_config`, `_datetime_to_string`,
`_datetime_from_weaviate_str`, and `_ServerVersion`. Sanitization removes
newlines and quotes a GraphQL string; beacon generation preserves input order;
timeouts must be positive; naive datetimes are interpreted as UTC with a
warning; nanosecond server timestamps truncate to Python microseconds.
`_ServerVersion.from_string` accepts one to three numeric components and its
comparisons and `is_at_least_any` follow semantic numeric ordering.

## Filter builders

Expose `weaviate.classes.query.Filter`. It is a non-instantiable factory with:

```python
Filter.by_property(name: str, length: bool = False)
Filter.by_id()
Filter.by_creation_time()
Filter.by_update_time()
Filter.by_ref(link_on: str)
Filter.by_ref_multi_target(link_on: str, target_collection: str)
Filter.by_ref_count(link_on: str)
Filter.all_of(filters: list)
Filter.any_of(filters: list)
Filter.not_(filter_)
```

Property builders support `is_none`, `equal`, `not_equal`, `less_than`,
`less_or_equal`, `greater_than`, `greater_or_equal`, `like`, `contains_any`,
`contains_all`, `contains_none`, and `within_geo_range`. The result retains a
target, value, and one of `Equal`, `NotEqual`, `LessThan`, `LessThanEqual`,
`GreaterThan`, `GreaterThanEqual`, `Like`, `IsNull`, `ContainsAny`,
`ContainsAll`, `ContainsNone`, or `WithinGeoRange`.

`length=True` wraps the property target as `len(name)`. ID filters normalize
UUIDs. Reference chains preserve link order and capitalize the first letter of
a multi-target collection. Empty value lists and empty `all_of`/`any_of`
groups raise `WeaviateInvalidInputError`. One-element groups return that
element. `&`, `|`, and `~` create nested AND, OR, and NOT filter nodes in stable
input order. Calling `Filter()` directly raises `TypeError`.

## Query builders

Under `weaviate.classes.query`, implement:

```python
MetadataQuery(creation_time=False, last_update_time=False, distance=False,
              certainty=False, score=False, explain_score=False,
              is_consistent=False, query_profile=False)
MetadataQuery.full() -> MetadataQuery
MetadataQuery.full_with_profile() -> MetadataQuery
Sort.by_property(name: str, ascending: bool = True)
Sort.by_id(ascending: bool = True)
Sort.by_creation_time(ascending: bool = True)
Sort.by_update_time(ascending: bool = True)
GroupBy(prop: str, objects_per_group: int, number_of_groups: int)
Rerank(prop: str, query: str | None = None)
Move(force: float, objects=None, concepts=None)
Diversity.mmr(limit: int | None = None, balance: float | None = None)
BM25Operator.or_(minimum_match: int)
BM25Operator.and_()
BM25Operator.and_cross()
```

`full()` enables every ordinary metadata field but leaves query profiling off;
`full_with_profile()` also enables profiling. Sort builders return a mutable
chain whose calls append stable `(property, ascending)` entries. `Sort()` is
not directly instantiable. `Move` requires at least one object or concept,
normalizes scalar inputs to lists, and emits the documented GraphQL payload.

Provide `Boost` with `filter`, `time_decay`, `numeric_decay`,
`numeric_property`, and `blend`. Time-decay datetimes become RFC 3339 strings;
whole `timedelta` values choose day, hour, minute, then second suffixes.
Supported curves are `exp`, `gauss`, and `linear`; numeric-property modifiers
are `log1p` and `sqrt`. `blend` preserves condition order, carries each child
weight into its condition, rejects an empty input and child-level depth, and
applies top-level weight/depth.

## Collection configuration

Expose `weaviate.classes.config` with `DataType`, `Tokenization`,
`VectorDistances`, `Property`, `ReferenceProperty`, `Configure`, and
`Reconfigure`.

```python
Property(name: str, data_type: DataType, description: str | None = None,
         index_filterable: bool | None = None,
         index_searchable: bool | None = None,
         index_range_filters: bool | None = None,
         nested_properties: Property | list[Property] | None = None,
         skip_vectorization: bool = False,
         text_analyzer=None, tokenization: Tokenization | None = None,
         vectorize_property_name: bool = True)
ReferenceProperty(name: str, target_collection: str,
                  description: str | None = None)
ReferenceProperty.MultiTarget(name: str, target_collections: list[str],
                              description: str | None = None)
```

Property wire dictionaries use `dataType` as a one-item list, recursively
serialize nested properties, and preserve explicit index flags. `vector` is a
reserved property name. Reference target collection names have only their
first character capitalized and serialize under `dataType`.

Implement these configuration factories and their server-facing camelCase
serialization:

```python
Configure.text_analyzer(ascii_fold=None, ascii_fold_ignore=None,
                        stopword_preset=None)
Configure.inverted_index(bm25_b=None, bm25_k1=None,
                         cleanup_interval_seconds=None,
                         index_timestamps=None, index_property_length=None,
                         index_null_state=None, stopwords_preset=None,
                         stopwords_additions=None, stopwords_removals=None,
                         stopword_presets=None)
Configure.multi_tenancy(enabled=True, auto_tenant_creation=None,
                        auto_tenant_activation=None)
Configure.replication(factor=None, async_enabled=None,
                      deletion_strategy=None, async_config=None)
```

BM25 `b` and `k1` must be specified together. ASCII-fold ignore characters
require ASCII folding. Omit unspecified fields from wire dictionaries while
retaining required server defaults such as the stopword object.

Provide `Configure.VectorIndex` factories `none`, `hnsw`, `flat`, `dynamic`,
and `hfresh`, plus `Configure.VectorIndex.Quantizer.pq`, `bq`, `sq`, `rq`, and
`none`. Preserve distance values and camelCase fields. Quantizer wire blocks
are named `pq`, `bq`, `sq`, or `rq` and default to enabled. HFresh accepts only
rotational quantization and supports `distance_metric`,
`max_posting_size_kb`, `replicas`, `search_probe`, and optional multi-vector
configuration.

For updates, provide `Reconfigure.VectorIndex.hfresh(max_posting_size_kb=None,
search_probe=None, quantizer=None)` and
`Reconfigure.VectorIndex.Quantizer.rq(rescore_limit=None, enabled=True,
bits=None)`. When merging an HFresh named-vector update into existing server
configuration, update the existing `rq` block without assuming a `pq` block
exists. Preserve unrelated distance, posting-size, search-probe, enabled, and
bits fields. Attempting to switch away from an already enabled incompatible
quantizer remains an input error.

# Implementation Notes

- Keep module paths and re-exports compatible; callers import both root names
  and `weaviate.classes.init`, `weaviate.classes.query`,
  `weaviate.classes.config`, `weaviate.connect.base`, and `weaviate.util`.
- Pydantic models should reject unknown fields where the corresponding public
  contract is strict and retain aliases needed for camelCase server payloads.
- Preserve enum values, dataclass/Pydantic field values, exception types, and
  deterministic ordering. Do not replace exceptions with sentinel strings.
- Package metadata is part of the contract. A static version is acceptable;
  a setuptools-scm build must also succeed from a source archive when the
  standard `SETUPTOOLS_SCM_PRETEND_VERSION` environment variable is supplied.
- Do not connect to a database or exercise root connection helpers while
  importing. Embedded Weaviate download/startup behavior is outside this
  offline task and must not run implicitly.
- Do not copy upstream source or tests. Implement the behavior from this
  specification in ordinary package files.
