# Build `yarl`

## Project Description

Implement an installable Python package named `yarl` that provides an immutable
`URL` value object for parsing, canonicalizing, inspecting, and transforming
absolute and relative URLs. The target contract follows `yarl` 1.24.5 on
CPython 3.12.

URL components are stored canonically: hosts use IDNA ASCII form, while user
information, paths, queries, and fragments use UTF-8 percent encoding. Public
decoded properties expose human text and corresponding `raw_` properties expose
encoded text. All transformations return URL objects and do not mutate the
receiver.

## Supports

- Python 3.10 or newer; the verifier uses CPython 3.12.
- An installable `yarl` distribution with `yarl.__version__ == "1.24.5"`.
- Runtime dependencies compatible with `idna>=2.0`, `multidict>=4.0`, and
  `propcache>=0.2.1`.
- The documented pure-Python build mode selected by `YARL_NO_EXTENSIONS=1`.
  A compiled extension is optional and must not change public behavior.
- Absolute URLs of the form
  `[scheme:]//[user[:password]@]host[:port][/path][?query][#fragment]` and
  relative URLs of the form `[/path][?query][#fragment]`.
- Deterministic local behavior. Parsing and transformation require no network,
  DNS, filesystem, subprocess, random, locale, or wall-clock access.

## API Usage Guide

### Package exports

`yarl.__all__` is the ordered tuple:

```python
("URL", "SimpleQuery", "QueryVariable", "Query",
 "cache_clear", "cache_configure", "cache_info")
```

`SimpleQuery`, `QueryVariable`, and `Query` are public typing aliases describing
accepted query values and query containers. They must be importable from
`yarl`. `URL.__module__` is `"yarl"`.

### Construction

```python
URL(
    val: str | urllib.parse.SplitResult | URL = "",
    *,
    encoded: bool = False,
    strict: bool | None = None,
) -> URL
```

`URL()` constructs the empty relative URL. Passing an existing `URL` returns
the same immutable object. Strings are parsed and canonicalized unless
`encoded=True`, in which case already encoded component bytes are preserved.
A `SplitResult` is accepted only with `encoded=True`; applying normal decoding
to a `SplitResult` raises `ValueError`. `strict` is retained for compatibility
and may issue a deprecation warning.

```python
URL.build(
    *,
    scheme: str = "",
    authority: str = "",
    user: str | None = None,
    password: str | None = None,
    host: str = "",
    port: int | None = None,
    path: str = "",
    query: Query | None = None,
    query_string: str = "",
    fragment: str = "",
    encoded: bool = False,
) -> URL
```

`build()` constructs from components. `authority` cannot be combined with
`user`, `password`, `host`, or `port`. `query` and `query_string` are mutually
exclusive. User information or a port without a host is invalid. Invalid
combinations raise `ValueError`.

```python
from yarl import URL

url = URL("https://user:pass@пример.рф:8443/a b?x=1#часть")
assert str(url) == (
    "https://user:pass@xn--e1afmkfd.xn--p1ai:8443/"
    "a%20b?x=1#%D1%87%D0%B0%D1%81%D1%82%D1%8C"
)
assert url.human_repr() == "https://user:pass@пример.рф:8443/a b?x=1#часть"
```

### Representation and value semantics

The following data-model methods are supported:

```python
str(url) -> str
repr(url) -> str                 # URL('...')
bytes(url) -> bytes              # ASCII canonical URL bytes
bool(url) -> bool
hash(url) -> int
url1 == url2 -> bool
url1 < url2, <=, >, >= -> bool   # URL-to-URL lexical ordering
url / segment -> URL
url % query -> URL
```

URLs compare equal and hash equally when their canonical components match.
Equality with an unrelated type is false; ordering with an unrelated type
raises `TypeError`. `/` appends one encoded path segment and rejects a segment
that begins with `/`. `%` is an alias for `with_query`.

### Authority and identity

The following read-only properties and methods are available:

```python
url.absolute: bool
url.scheme: str
url.raw_authority: str
url.authority: str
url.raw_user: str | None
url.user: str | None
url.raw_password: str | None
url.password: str | None
url.raw_host: str | None
url.host: str | None
url.host_subcomponent: str | None
url.host_port_subcomponent: str | None
url.port: int | None
url.explicit_port: int | None

url.is_absolute() -> bool
url.is_default_port() -> bool
url.origin() -> URL
url.relative() -> URL
```

`host` is decoded Unicode and `raw_host` is canonical IDNA text. IPv6 host
subcomponents include brackets where required. `port` substitutes the standard
default for known schemes, while `explicit_port` reports only a written port.
`origin()` returns only scheme and authority and rejects relative URLs.
`relative()` removes scheme and authority while retaining path, query, and
fragment.

### Path, query, and fragment properties

```python
url.raw_path: str
url.path: str
url.path_safe: str
url.raw_query_string: str
url.query_string: str
url.query: multidict.MultiDictProxy[str]
url.raw_fragment: str
url.fragment: str
url.raw_path_qs: str
url.path_qs: str

url.raw_parts: tuple[str, ...]
url.parts: tuple[str, ...]
url.parent: URL
url.raw_name: str
url.name: str
url.raw_suffix: str
url.suffix: str
url.raw_suffixes: tuple[str, ...]
url.suffixes: tuple[str, ...]
```

`query` preserves insertion order and duplicate keys. `parts`, names, and
suffixes use decoded text; their `raw_` counterparts use encoded text.
`parent` drops the final path segment and clears query and fragment.

### Immutable component transforms

```python
url.with_scheme(scheme: str) -> URL
url.with_user(user: str | None) -> URL
url.with_password(password: str | None) -> URL
url.with_host(host: str) -> URL
url.with_port(port: int | None) -> URL
url.with_path(
    path: str,
    *,
    encoded: bool = False,
    keep_query: bool = False,
    keep_fragment: bool = False,
) -> URL
url.with_fragment(fragment: str | None) -> URL
url.with_name(
    name: str,
    *,
    keep_query: bool = False,
    keep_fragment: bool = False,
) -> URL
url.with_suffix(
    suffix: str,
    *,
    keep_query: bool = False,
    keep_fragment: bool = False,
) -> URL
```

`None` clears user, password, port, or fragment where accepted. Clearing the
user also clears the password. Host transformations IDNA-encode Unicode.
Authority transforms require an absolute URL. Ports must be integers in the
valid range or `None`. By default path/name/suffix changes clear query and
fragment; the `keep_` flags retain them. Names cannot contain `/`. A non-empty
suffix must start with `.`.

### Query transforms

```python
url.with_query(query: Query | None = None, **kwargs: QueryVariable) -> URL
url.extend_query(query: Query | None = None, **kwargs: QueryVariable) -> URL
url.update_query(query: Query | None = None, **kwargs: QueryVariable) -> URL
url.without_query_params(*query_params: str) -> URL
```

Each query method accepts exactly one positional query or keyword parameters.
A query can be a raw query string, a mapping, or an ordered iterable of
`(key, value)` pairs. Scalar values are `str`, `int`, or `float`; `bool` is
rejected. Mapping values may be lists or tuples of scalar values to represent
duplicates. Unsupported or nested values raise `TypeError`, and multiple
positional query arguments raise `ValueError`.

- `with_query` replaces the entire query; `None` clears it.
- `extend_query` appends all new pairs and preserves duplicate existing keys.
  Passing `None` returns the same immutable object.
- `update_query` removes existing values for each supplied key, then writes the
  replacement values while retaining other keys. Passing `None` returns the
  same object.
- `without_query_params` removes every pair whose key is named. If no key is
  present it returns the same object.

### Joining

```python
url.join(other: URL) -> URL
url.joinpath(*other: str, encoded: bool = False) -> URL
url.human_repr() -> str
```

`join` resolves a URL reference using RFC 3986 semantics, including network
references, root paths, dot segments, queries, and fragments. `joinpath`
appends path segments and rejects any segment beginning with `/`.
`human_repr()` decodes IDNA and safe percent-encoded text for display while
preserving URL meaning.

### Cache controls

```python
cache_clear() -> None
cache_info() -> dict[str, functools._CacheInfo]
cache_configure(
    *,
    idna_encode_size: int | None = 256,
    idna_decode_size: int | None = 256,
    ip_address_size: int | None = 512,
    host_validate_size: int | None = 512,
    encode_host_size: int | None = 512,
) -> None
```

The cache-info mapping has the ordered keys `idna_encode`, `idna_decode`,
`ip_address`, `host_validate`, and `encode_host`; each value exposes standard
`hits`, `misses`, `maxsize`, and `currsize` fields. Configuration replaces the
corresponding LRU caches, and `cache_clear` resets their statistics and entries.

### Errors and optional integrations

Malformed bracketed IPv6 hosts, non-numeric ports, out-of-range ports, colons
inside an unbracketed host argument, invalid component combinations, and
forbidden relative-authority transforms raise `ValueError`. Wrong argument
types raise `TypeError`.

`URL` supports `copy.copy`, `copy.deepcopy`, and pickle round trips while
preserving equality. When Pydantic 2 is installed, `URL` is accepted as a model
field and by `TypeAdapter(URL)`; strings are parsed into `URL` instances and
invalid non-string inputs produce Pydantic validation errors.

## Implementation Notes

Keep the public imports and signatures above stable. Preserve duplicate query
ordering, default-port substitution, percent-encoding case, dot-segment
normalization, object identity for documented no-op transforms, exact exception
classes, and deterministic cache behavior.

The implementation may use pure Python and the declared runtime dependencies.
It must not import a separately installed copy of `yarl`, retrieve upstream
source, or contact a network service. Hidden evaluation invokes candidate code
only in bounded unprivileged subprocesses; the trusted verifier owns expected
values, collection records, grading, and reward output.
