# Build `furl`
Create a complete, installable Python package named `furl` from an empty workspace. It is a local URL parsing and manipulation library. The package must run on CPython 3.12 without network access after its declared build-time dependencies have been installed.
## Project Description
The package models a URL as coordinated scheme, authority, path, query, and fragment components. It preserves ordered repeated query parameters, supports percent encoding and IDNA hostnames, and exposes both component objects and a convenient `furl` facade. All operations are deterministic and local. The library must not contact a network, invoke a subprocess, or require a service.
## Supports
- Provide an installable source-only package with a `furl` package directory, `__init__.py`, `__version__.py`, and package metadata.
- Use Python 3.12 and the runtime dependencies `six` and `orderedmultidict`. The test runner is pytest, but pytest must not be a runtime dependency of the library itself.
- Match the metadata constants `__title__`, `__version__`, `__license__`, `__author__`, `__contact__`, `__url__`, `__copyright__`, and `__description__` exposed by the package. The version is `2.1.4` and the license is the Unlicense.
- Preserve insertion order for path segments and repeated query parameters. Do not use network, filesystem, subprocess, current time, or randomness to implement URL behavior.
- The public behavior is the documented component API below. Private helper names and the exact internal representation are not part of the contract.
## API Usage Guide
### Package exports and helpers
`from furl import furl` imports the main class. The root package also re-exports the public names from `furl.furl`, including `Path`, `Query`, `Fragment`, `omdict1D`, `urlsplit`, `urljoin`, `join_path_segments`, `remove_path_segments`, `is_valid_port`, `is_valid_scheme`, `is_valid_host`, `is_valid_encoded_path_segment`, `is_valid_encoded_query_key`, and `is_valid_encoded_query_value`.
The helper signatures are:
```text
lget(lst, index, default=None)
attemptstr(value)
utf8(value, default=_absent)
non_string_iterable(value)
idna_encode(value)
idna_decode(value)
is_valid_port(port)
static_vars(**kwargs)
create_quote_fn(safe_charset, quote_plus)
get_scheme(url)
strip_scheme(url)
set_scheme(url, scheme)
has_netloc(url)
urlsplit(url)
urljoin(base, url)
join_path_segments(*segments)
remove_path_segments(segments, remove)
quacks_like_a_path_with_segments(value)
```
Validation helpers return booleans. Port values are valid only when their decimal value is in `1..65535`. Scheme validation accepts an initial ASCII letter followed by ASCII letters, digits, `-`, `.`, or `+`. Host validation rejects empty labels, adjacent periods, and the documented punctuation while allowing valid IPv4/IPv6 forms. `urlsplit` returns an `urllib.parse.SplitResult`-compatible tuple with `scheme`, `netloc`, `path`, `query`, and `fragment` fields. `urljoin` follows the library's scheme-aware URL joining behavior. Path-segment helpers return lists and preserve the special empty segment that represents a slash.
### `Path`
Import path: `from furl.furl import Path`.
```text
Path(path='', force_absolute=lambda _: False, strict=False)
load(path) -> self
add(path) -> self
set(path) -> self
remove(path) -> self
normalize() -> self
asdict() -> dict
```
`path` may be a string, a list of segments, or another path-like object with `segments`. `segments` contains decoded strings; `str(path)` percent-encodes each segment and joins them with `/`. Empty paths, leading and trailing slashes, Unicode, and already encoded input remain distinguishable. `isabsolute` is readable and normally settable; it is forced and read-only when a URL has a netloc. `isdir` is true for an empty path or a trailing empty segment, and `isfile` is its inverse. `Path` supports truth testing, equality by string form, `repr`, and `/` composition; division returns a copy and does not mutate the original.
### `Query` and `omdict1D`
Import paths: `from furl.furl import Query` and `from furl.omdict1D import omdict1D`.
```text
Query(query='', strict=False)
Query.load(query) -> self
Query.add(args) -> self
Query.set(mapping) -> self
Query.remove(query) -> self
Query.encode(delimiter='&', quote_plus=True, dont_quote='', delimeter=_absent) -> str
Query.asdict() -> dict
```
`Query.params` is an ordered multivalue mapping and `Query.args` is an alias to it. Query strings decode `+` as a space, preserve repeated keys and key-only parameters (`None` values), and encode keys and values according to `delimiter`, `quote_plus`, and `dont_quote`. The misspelled `delimeter` keyword remains accepted and overrides `delimiter` when supplied. `load`, `add`, `set`, and `remove` accept query strings, mappings, ordered multivalue mappings, or key/value iterables. They return `self`; boolean conversion reflects whether parameters exist.
`omdict1D` subclasses `orderedmultidict.omdict`. Its `add`, `set`, `__setitem__`, `update`, and `updateall` treat iterable non-string values as multiple values, while scalar values remain one value. Inherited `getlist`, `allitems`, and ordered mapping behavior remain available.
### `Fragment`
Import path: `from furl.furl import Fragment`.
```text
Fragment(fragment='', strict=False)
load(fragment) -> self
add(path=_absent, args=_absent) -> self
set(path=_absent, args=_absent, separator=_absent) -> self
remove(fragment=_absent, path=_absent, args=_absent) -> self
asdict() -> dict
```
Fragments contain a path and query, optionally separated by `?`. `path`, `query`, and `args` expose those component objects. `separator` controls whether `?` is emitted between a nonempty fragment path and query. Fragment operations mutate and return `self`, preserve ordering and encoding, and support `str`, `repr`, equality, and truth testing.
### `furl`
Import path: `from furl import furl`.
```text
furl(url='', args=_absent, path=_absent, fragment=_absent, scheme=_absent, netloc=_absent, origin=_absent, fragment_path=_absent, fragment_args=_absent, fragment_separator=_absent, host=_absent, port=_absent, query=_absent, query_params=_absent, username=_absent, password=_absent, strict=False)
load(url) -> self
add(args=_absent, path=_absent, fragment_path=_absent, fragment_args=_absent, query_params=_absent) -> self
set(args=_absent, path=_absent, fragment=_absent, query=_absent, scheme=_absent, username=_absent, password=_absent, host=_absent, port=_absent, netloc=_absent, origin=_absent, query_params=_absent, fragment_path=_absent, fragment_args=_absent, fragment_separator=_absent) -> self
remove(args=_absent, path=_absent, fragment=_absent, query=_absent, scheme=False, username=False, password=False, host=False, port=False, netloc=False, origin=False, query_params=_absent, fragment_path=_absent, fragment_args=_absent) -> self
tostr(query_delimiter='&', query_quote_plus=True, query_dont_quote='') -> str
join(*urls) -> self
copy() -> furl
asdict() -> dict
```
The instance exposes `path`, `query`, `fragment`, `args`, `scheme`, `username`, `password`, `host`, `port`, `netloc`, `origin`, and `url` properties. Component assignment updates the URL and preserves consistency. Host and scheme values are normalized to lowercase; default ports for recognized schemes are omitted from the serialized netloc but remain available through `port`. Username and password are percent-encoded in the netloc. `url`, `str(instance)`, and `tostr()` serialize the complete URL deterministically.
`add` appends path/query/fragment data. `set` replaces supplied components and returns the same instance; overlapping aliases such as `args` and `query_params` may emit `UserWarning`, with the more specific arguments taking precedence. `remove` deletes only requested components; `True` removes a whole component. Failed component assignments must not leave a partially modified URL. `join` applies URL joining successively and `copy` returns an independent equivalent object. `asdict` contains the serialized URL and component dictionaries.
Malformed ports, invalid hosts, malformed IPv6 literals, and invalid component values raise ordinary `ValueError` without silently changing unrelated state. On the locked modern Python runtime, bracketed host validation follows `urllib.parse` and may raise `ValueError` for malformed IPv6 input.
## Implementation Notes
- Keep modules separated into `furl.furl`, `furl.omdict1D`, `furl.compat`, and `furl.common`, and preserve public re-exports and metadata identity.
- Use `orderedmultidict.omdict` rather than replacing it with an unordered mapping. Preserve repeated-query order and list-valued update semantics.
- Use standard-library URL parsing and quoting consistently. Do not add a network client, subprocess fallback, cache service, or runtime source fetch.
- The frozen verifier exercises path normalization and division, query encoding and repeated values, fragment separators, URL component mutation, usernames/passwords, IDNA, validation helpers, URL joining/splitting, dictionaries, equality, metadata, and `omdict1D` updates. It runs the portable subset of the upstream tests in an unprivileged child process.
- Three historical assertions depend on pre-modern `urllib.parse` behavior for malformed bracketed IPv6 and four-leading-slash round trips. They are excluded from the frozen collection because the task locks modern Python; this is recorded in private provenance, while all remaining upstream behavior is tested unchanged.
