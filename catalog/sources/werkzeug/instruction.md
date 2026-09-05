# Build `werkzeug`

Create a complete installable Python project named `Werkzeug` from an empty
workspace. The distribution must provide the `werkzeug` package using a `src/`
layout and must not rely on a preinstalled copy of Werkzeug or on network access
at runtime. Use only the Python standard library plus the declared runtime
dependency `MarkupSafe`.

## Project Description

Werkzeug is a WSGI and HTTP utility library. This task focuses on the
deterministic core used by web applications: ordered multi-value mappings,
HTTP header and cookie parsing, URL IRI/URI conversion, password helpers,
WSGI stream and environment helpers, routing, and the sans-IO request/response
objects. The implementation is a library, not a running web service. Do not
add a network client, database, browser, or external service integration.

## Natural Language Instruction

Create the `werkzeug` project from an empty workspace. Implement deterministic
multi-value data structures, HTTP header/cookie and URL helpers, safe path and
password functions, WSGI stream/environment utilities, sans-IO request and
response objects, wrappers, a local test client, and routing. Preserve public
import paths, ordering, protocol behavior, and documented exception classes.

## Supports

- Support CPython 3.10 and newer 3.x versions in ordinary use.
- Provide an installable `src/werkzeug/` package and package metadata.
- `import werkzeug` and the documented submodules must work in a fresh target
  installation with no repository tests present.
- Preserve the public import paths and ordinary Python protocol behavior.
- Keep deterministic operations local. The verifier uses in-memory streams,
  fixed WSGI environments, fixed dates, and a local WSGI application.
- Do not expose or depend on hidden tests, the reference source, or a generated
  reward file.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
└── src/
    └── werkzeug/
        ├── __init__.py
        ├── datastructures/
        ├── http.py
        ├── urls.py
        ├── security.py
        ├── wsgi.py
        ├── routing/
        ├── sansio/
        ├── wrappers/
        └── test.py
```

The source layout may be equivalent, but each module named in the API guide
must be importable after installation. Do not add a live server, network
client, browser integration, or external service.

## API Usage Guide

### Data structures

Import `MultiDict`, `ImmutableMultiDict`, `CombinedMultiDict`, `Headers`,
`EnvironHeaders`, `Accept`, `MIMEAccept`, `LanguageAccept`, `ETags`,
`Authorization`, `FileStorage`, `TypeConversionDict`, and `HeaderSet` from
`werkzeug.datastructures`.

`MultiDict(mapping_or_pairs=None)` preserves all values for a key while normal
mapping lookup returns the first value. `getlist(key, type=None)` returns all
values, optionally converting each value and omitting values whose conversion
raises `ValueError` or `TypeError`. `setlist(key, values)` replaces the values;
`add(key, value)` appends one value; `items(multi=True)` yields every pair in
insertion order; `to_dict(flat=True)` returns the first value per key and
`flat=False` returns lists. `update` appends values from another mapping or
multi-value mapping. Missing keys raise `KeyError` for indexing and return the
given default from `get`.

`ImmutableMultiDict` has the same read behavior but rejects mutation. Its
`copy()` returns a mutable `MultiDict`. `CombinedMultiDict` reads from its
component mappings in order. `TypeConversionDict.get(key, default=None, type=None)`
returns the converted value or the default when conversion fails.

`Headers(mapping_or_pairs=None)` is an ordered, case-insensitive header
collection. Assignment replaces all values for a name, `add` appends a value,
`getlist` returns all values, and `to_wsgi_list()` returns `(name, value)` pairs
with their current display names. Header names compare case-insensitively but
values retain their text. `EnvironHeaders` exposes HTTP headers from a WSGI
environment without allowing mutation. `HeaderSet` provides case-insensitive
set-like membership and ordered values.

`Accept.from_header(value)` parses quality-weighted values and
`best_match(matches, default=None)` selects the best matching candidate,
honoring quality, specificity, and input order. `MIMEAccept` understands media
type wildcards and exposes `accept_html`, `accept_xhtml`, and `accept_json`.
`LanguageAccept` applies language-prefix matching. `ETags.from_header(value)`
parses strong, weak, and wildcard tags; `contains`, `contains_weak`,
`contains_raw`, `is_strong`, `is_weak`, `to_header`, and `as_set` retain their
distinctions.

`Authorization.from_header(value)` parses Basic and token-style authorization
headers and `to_header()` serializes the object. `FileStorage(stream, filename,
name=None, content_type=None)` wraps a file-like object; `save(dst)` copies
bytes to a file-like destination and `close()` closes the wrapped stream.

### HTTP and URLs

Import `parse_list_header`, `dump_header`, `parse_dict_header`,
`parse_options_header`, `dump_options_header`, `quote_etag`, `unquote_etag`,
`generate_etag`, `parse_cookie`, `dump_cookie`, `parse_date`, and `http_date`
from `werkzeug.http`.

List headers accept quoted values and commas; dict headers parse key/value
options and bare keys; option headers return `(main_value, parameters)` and
must correctly handle quoted and extended parameter values. The dump functions
produce valid deterministic header text. ETags use quoted values and preserve
the weak marker. `generate_etag(data)` returns the lowercase hexadecimal SHA-1
digest of bytes. `parse_date` returns an aware UTC datetime or `None`, while
`http_date` formats a timestamp or datetime as an RFC 1123 HTTP date. Cookie
parsing returns a `TypeConversionDict`-like mapping and `dump_cookie` serializes
the supplied attributes without inventing an unrelated cookie.

Import `iri_to_uri(iri)` and `uri_to_iri(uri)` from `werkzeug.urls`. Convert
Unicode hostnames and path/query text using the standard URI percent-encoding
rules. Valid ASCII URI escapes remain stable; malformed escapes are handled
without crashing. Conversion is idempotent for already-converted values.

### Security and WSGI helpers

`werkzeug.security.safe_join(directory, *pathnames)` returns a normalized path
inside `directory`, or `None` for absolute paths, traversal, alternate
separators, or other escapes. `generate_password_hash(password, method="scrypt",
salt_length=16)` returns a self-contained encoded hash; `check_password_hash`
returns `True` only for the original password and `False` for a wrong one.

`werkzeug.wsgi.get_host(environ, trusted_hosts=None, x_host=None)` selects the
validated host from the WSGI environment and `get_current_url(environ, ... )`
constructs the current URL with correct scheme, host, script root, path, and
query escaping. `get_content_length` parses a valid nonnegative content length.
`LimitedStream(stream, limit, is_max=False)` exposes at most `limit` bytes,
supports `read`, iteration, `tell`, and `exhaust`, and raises the documented
disconnect error when the wrapped stream ends before a required maximum.

### Sans-IO request, response, and routing

`werkzeug.sansio.request.Request(method="GET", scheme="http", server=None,
root_path=None, path="/", query_string="", headers=None, remote_addr=None)`
stores request metadata and exposes `url`, `base_url`, `root_url`, `host_url`,
`host`, `full_path`, `is_secure`, `args`, `cookies`, `content_length`,
`mimetype`, `mimetype_params`, `accept_mimetypes`, `if_match`, `range`, and
`is_json` with lazy deterministic parsing.

`werkzeug.sansio.response.Response(status=None, headers=None)` stores status
and headers. The `status_code`, `status`, `mimetype`, `mimetype_params`,
`is_json`, `content_md5`, `cache_control`, `content_range`, `www_authenticate`,
and `content_security_policy` properties parse and serialize their respective
headers. `set_cookie(key, value="", max_age=None, expires=None, path="/", ... )`
adds a correctly formatted Set-Cookie header and `delete_cookie` expires one.

`werkzeug.wrappers.Request` and `werkzeug.wrappers.Response` adapt these
objects to WSGI. `Response(response=None, status=None, headers=None,
... )` accepts text or bytes and `get_data(as_text=False)` returns the body.
`Request.from_values(...)` creates a request from query/form values. The
`werkzeug.test.Client(application, response_wrapper=None, use_cookies=True)`
client can call `get` and `post` against a local WSGI callable; responses
expose status, headers, data, and text.

`werkzeug.routing.Map(rules=None, converters=None, ...).bind(server_name,
script_name="", subdomain=None, url_scheme="http", default_method="GET",
path_info=None, query_args=None)` returns a `MapAdapter`. `Rule(rule,
defaults=None, subdomain=None, methods=None, ... )` declares a route. The
adapter's `match(path_info, method="GET", ...)` returns `(endpoint, values)`
or raises the documented routing exception; `build(endpoint, values=None,
method="GET", force_external=False, ...)` returns a URL and rejects unknown
endpoints or incompatible methods.

## Implementation Notes

- Keep the package importable without the hidden verifier files.
- Preserve ordering and case rules; do not replace multi-value collections with
  plain dictionaries.
- Converters and validators must reject malformed input through the documented
  exception types rather than silently returning a plausible value.
- The test client must close request and response streams and preserve cookie
  behavior between requests while `use_cookies=True`.
- Implement the documented public surface across modules, including exports and
  exception classes. Avoid hard-coding only the examples above.

## Examples

```python
from werkzeug.datastructures import MultiDict, Headers

values = MultiDict([('tag', 'one'), ('tag', 'two')])
assert values.getlist('tag') == ['one', 'two']
headers = Headers([('X-Test', 'yes')])
assert headers['x-test'] == 'yes'
```

```python
from werkzeug.routing import Map, Rule

routes = Map([Rule('/users/<int:id>', endpoint='user')])
adapter = routes.bind('example.test')
assert adapter.match('/users/7') == ('user', {'id': 7})
```

## Error Handling and Boundary Conditions

- Multi-value collections preserve insertion order and reject mutation through
  immutable variants; conversion failures return the requested default.
- Header, cookie, URL, and routing parsers reject malformed values with their
  documented exception or `None` result rather than inventing data.
- `safe_join` returns `None` for traversal, absolute, or alternate-separator
  escapes. Password verification is deterministic in truth value but must not
  expose a stored secret.
- WSGI streams enforce their byte limit and request/response wrappers close
  local streams. Runtime execution is NoNetwork and has no live server.
