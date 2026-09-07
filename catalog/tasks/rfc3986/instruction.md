# Build `rfc3986`

Create a complete, installable Python project named `rfc3986` from an empty
workspace. It parses and validates URI references according to RFC 3986 and
provides an IRI encoder plus a small builder and `urlparse` compatibility API.
The implementation must be local and deterministic; do not fetch source code
or dependencies during evaluation.

## Natural Language Instruction

Build the installable `rfc3986` library from an empty workspace. Implement URI
and IRI parsing, normalization, resolution, validation, persistent URI builders,
and standard-library-compatible parse result objects described below. Preserve
component presence distinctions and exception behavior exactly. This is a
local pure-Python API: parsing and validation never make network requests.

## Project Description

The package accepts URI/IRI strings or bytes, exposes their components, can
normalize them, resolves relative references against absolute bases, and
validates component presence and syntax. It also provides `URIBuilder` for
constructing references, `ParseResult` compatibility objects, and helper
functions for component normalization.

## Supports

- Support CPython 3.12 and newer Python 3.x versions compatible with the
  package contract. Use a `src/rfc3986/` package layout and an installable
  setuptools build from `setup.py`/`setup.cfg` or an equivalent PEP 517 build.
- The distribution is `rfc3986`, version `2.0.0`, licensed Apache-2.0. Runtime
  behavior uses the standard library only. The optional `idna` package may be
  used when explicitly installed, but it is not required for ordinary URI
  behavior.
- Expose the root names `ParseResult`, `URIReference`, `IRIReference`,
  `is_valid_uri`, `normalize_uri`, `uri_reference`, `iri_reference`,
  `urlparse`, and the release metadata constants.
- Preserve component order and deterministic string/bytes behavior. Parsed
objects are immutable named-tuple-like values with components
  `scheme`, `authority`, `path`, `query`, and `fragment`.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
└── src/
    └── rfc3986/
        ├── __init__.py
        ├── api.py
        ├── uri.py
        ├── iri.py
        ├── parseresult.py
        ├── builder.py
        ├── normalizers.py
        ├── validators.py
        ├── misc.py
        └── exceptions.py
```

The distribution is installed from the workspace root and public imports
resolve from `src/rfc3986`. Keep package metadata and the standard-library-only
runtime boundary consistent with this tree.

## API Usage Guide

Public functional imports include `from rfc3986.api import uri_reference,
iri_reference, is_valid_uri, normalize_uri, urlparse`; classes are imported
from `rfc3986.uri`, `rfc3986.iri`, `rfc3986.parseresult`, and
`rfc3986.builder` as specified below.

### Functional API

`rfc3986.api.uri_reference(uri, encoding="utf-8")` returns a
`URIReference`. `rfc3986.api.iri_reference(iri, encoding="utf-8")` returns an
`IRIReference`. Both accept `str` or bytes and percent-encode non-ASCII
components using the selected encoding.

`rfc3986.api.is_valid_uri(uri, encoding="utf-8", **kwargs)` returns `bool`.
Supported keyword flags are `require_scheme`, `require_authority`,
`require_path`, `require_query`, and `require_fragment`. A flag requires that
component to be present and valid.

`rfc3986.api.normalize_uri(uri, encoding="utf-8")` returns the normalized URI
string. `rfc3986.api.urlparse(uri, encoding="utf-8")` returns a
`ParseResult` compatibility object.

### `URIReference`

Import path: `rfc3986.uri.URIReference`; construct with
`URIReference(scheme, authority, path, query, fragment, encoding="utf-8")` or
use `URIReference.from_string(uri_string, encoding="utf-8")`.

The `scheme`, `authority`, `path`, `query`, and `fragment` attributes are
strings or `None` (query and fragment preserve an explicitly empty component).
The read-only derived properties `userinfo`, `host`, and `port` parse the
authority; `authority_info()` returns a dict with those three keys and raises
`InvalidAuthority` for an invalid authority. `unsplit()` reconstructs the
reference without adding missing delimiters.

`normalize()` returns a new reference: schemes and hosts are lowercased,
percent escapes are uppercased, and dot path segments are removed. It does
not mutate the original. `is_absolute()` reports whether a scheme is present.
`is_valid(**kwargs)` is a deprecated convenience wrapper returning bool.
`copy_with(scheme=..., authority=..., path=..., query=..., fragment=...)`
returns a new reference; omitted values keep their old values.
`normalized_equality(other)` compares normalized components.
`resolve_with(base_uri, strict=False)` resolves this relative reference
against an absolute base and raises `ResolutionError` if the base lacks a
scheme.

### `IRIReference`

Import path: `rfc3986.iri.IRIReference`. It has the same five components and
`from_string` behavior as `URIReference`. `encode(idna_encoder=None)` returns
a `URIReference`, percent-encoding Unicode path/query/fragment and IDNA-
encoding Unicode host labels. A supplied encoder is called for each host
label. Invalid authority data raises the package exception contract.

### `ParseResult` and `ParseResultBytes`

Import path: `rfc3986.parseresult`. `ParseResult.from_string(uri,
encoding="utf-8", strict=True, lazy_normalize=True)` and
`ParseResult.from_parts(scheme=None, userinfo=None, host=None, port=None,
path=None, query=None, fragment=None, encoding="utf-8")` return a
seven-component tuple-like result in the order `scheme, userinfo, host, port,
path, query, fragment`. `urlparse` uses non-strict parsing.

`hostname`, `netloc`, `params`, and `geturl()` provide standard-library-style
access. `unsplit(use_idna=False)` reconstructs the URL. `copy_with(...)`
returns a new result, and `encode(encoding=None)` returns a
`ParseResultBytes` whose components and unsplit value are bytes.

### `URIBuilder`

Import path: `rfc3986.builder.URIBuilder`. The constructor accepts optional
`scheme`, `userinfo`, `host`, `port`, `path`, `query`, and `fragment` values.
`from_uri(reference)` accepts a reference or string. `add_scheme`,
`add_credentials`, `add_host`, `add_port`, `add_path`, `extend_path`,
`add_query_from`, `extend_query_with`, `add_query`, and `add_fragment` return
new builders and normalize their supplied component. Ports must be integers
from 0 through 65535. `finalize()` returns a `URIReference`; `geturl()`
returns its unsplit string.

### Normalization and validation helpers

`rfc3986.normalizers` exposes `normalize_scheme`, `normalize_authority`,
`normalize_username`, `normalize_password`, `normalize_host`,
`normalize_path`, `normalize_query`, `normalize_fragment`,
`normalize_percent_characters`, `remove_dot_segments`, and
`encode_component`. Percent escapes are preserved but canonicalized to upper
case; ordinary non-ASCII component bytes use `%XX` encoding.

`rfc3986.validators.Validator()` is configurable and mutable. Its methods
`allow_schemes`, `allow_hosts`, `allow_ports`, `allow_use_of_password`,
`forbid_use_of_password`, `check_validity_of`, and `require_presence_of`
return the validator for chaining. `validate(uri)` returns `None` on success
and raises `MissingComponentError`, `UnpermittedComponentError`,
`PasswordForbidden`, or `InvalidComponentsError` on failure. Module helpers
such as `host_is_valid`, `scheme_is_valid`, `path_is_valid`, `query_is_valid`,
`fragment_is_valid`, and `valid_ipv4_host_address` return booleans.

`rfc3986.misc.merge_paths(base_uri, relative_path)` merges a relative path
using RFC 3986 base-path rules. The component validator helpers return a
truthy regular-expression match object for a valid string and `None` for an
invalid or missing optional value; `valid_ipv4_host_address` returns a bool.
The exception classes are available from
`rfc3986.exceptions`, including `InvalidAuthority`, `InvalidPort`,
`ResolutionError`, and the validation errors.

## Implementation Notes

Keep the package importable without tests or documentation files. Preserve
`None` versus empty query/fragment delimiters, tuple-like equality and hashing,
authority parsing of userinfo/host/port including IPv6 literals, IDNA handling,
and the distinction between URI references and IRI references. Builder
operations are persistent: each `add_*` call returns a new builder and leaves
the original unchanged. Deprecated convenience methods may emit the standard
warnings but must retain their return values. Do not expose the hidden
verifier, its scenarios, or any reward/report files in the generated project.

## Examples

```python
from rfc3986.api import uri_reference, normalize_uri
reference = uri_reference('HTTP://Example.COM/a/../b?x=1')
assert reference.normalize().unsplit() == 'http://example.com/b?x=1'
assert normalize_uri('HTTP://Example.COM/a') == 'http://example.com/a'
```

```python
from rfc3986.builder import URIBuilder
uri = (URIBuilder().add_scheme('https').add_host('example.com')
       .add_path('/docs').add_query(foo='bar').finalize())
assert uri.unsplit() == 'https://example.com/docs?foo=bar'
```

```python
from rfc3986.api import is_valid_uri
assert is_valid_uri('https://example.com', require_scheme=True)
assert not is_valid_uri('relative/path', require_scheme=True)
```

## Error Handling and Boundary Conditions

`None` and empty query or fragment components remain distinguishable during
round trips. Invalid ports, malformed IPv6 authorities, forbidden password
usage, missing required components, and an unresolved base scheme raise the
documented exceptions rather than returning an altered URI. Builder calls are
persistent and do not mutate earlier builders. Bytes inputs preserve the
requested encoding and bytes result type. All operations run without DNS or
external-service access.
