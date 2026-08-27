# Project Description

Build an installable Python repository that implements the deterministic,
server-independent subset of the PyMongo and BSON APIs specified below. The
result is a local document/URI utility package, not a live database exercise:
no MongoDB server, DNS lookup, authentication service, or network connection is
required by the supported behavior.

The repository must install with `python -m pip install .` and expose both the
`bson` and `pymongo` import packages. Preserve the documented public import
paths, signatures, exception classes, result keys, and value shapes. A compiled
extension is optional; observable Python behavior is the contract.

## Supports

- Python 3.12 on Linux/amd64.
- A standard PEP 517 build configured by `pyproject.toml`.
- Distribution name `pymongo` and package version `4.18.0.dev0`.
- Runtime dependencies declared in project metadata. The evaluation runtime is
  offline, so supported calls must not fetch packages or contact a service.
- Public import packages `bson` and `pymongo` after installation.

Database clients, cursors, CRUD operations, server discovery, SRV/TXT DNS
resolution, authentication, encryption, GridFS, and monitoring are outside this
task.

## API Usage Guide

### Package Version

`pymongo.__version__` is the exact string `"4.18.0.dev0"`.

### JSON Utilities

#### `bson.json_util.dumps(obj: Any, *args: Any, **kwargs: Any) -> str`

For dictionaries, lists, strings, numbers, booleans, and `None`, return the
same JSON spelling as Python's default `json.dumps`: include the default spaces
after separators, preserve dictionary insertion order, and escape non-ASCII
characters by default. Nested values retain their shape.

Example:

```python
from bson import json_util

json_util.dumps({"second": 2, "first": "caf\u00e9"})
# '{"second": 2, "first": "caf\\u00e9"}'
```

#### `bson.json_util.loads(s: str | bytes | bytearray, *args: Any, **kwargs: Any) -> Any`

Parse JSON objects, arrays, strings, integers, floating-point numbers,
booleans, and null into their corresponding Python values. Leading and
trailing whitespace is accepted. Invalid JSON raises the underlying
`json.JSONDecodeError`; do not return a partial result.

### ObjectId Validation

#### `bson.objectid.ObjectId.is_valid(oid: Any) -> bool`

Return `True` for a 24-character hexadecimal string, accepting upper- or
lowercase hexadecimal digits. Return `False` for malformed values, including
wrong-length strings, non-hexadecimal text, 12-character text, integers, and
`None`. Validation does not raise for these malformed inputs.

### Host Parsing

#### `pymongo.uri_parser.parse_host(entity: str, default_port: int | None = 27017) -> tuple[str, int | None]`

Parse one host and return `(hostname, port)`. Lowercase the returned hostname.
Use `default_port` when no explicit port is present. Accept bracketed IPv6
literals and return the address without brackets. Explicit ports must be base-10
integers from 1 through 65535; zero, larger values, and non-numeric values raise
`ValueError`.

#### `pymongo.uri_parser.split_hosts(hosts: str, default_port: int | None = 27017) -> list[tuple[str, int | None]]`

Split a comma-separated host list in input order and apply `parse_host` to each
entry. Empty entries, including a doubled comma or a trailing comma, raise
`pymongo.errors.ConfigurationError`.

### MongoDB URI Parsing

#### `pymongo.uri_parser.parse_uri(uri: str, default_port: int | None = 27017, validate: bool = True, warn: bool = False, normalize: bool = True, connect_timeout: float | None = None, srv_service_name: str | None = None, srv_max_hosts: int | None = None) -> dict[str, Any]`

Support `mongodb://` URIs using literal hostnames, IPv4 addresses, bracketed
IPv6 addresses, and comma-separated host lists. This task does not require
`mongodb+srv://` or DNS resolution.

The returned dictionary has exactly these keys:

- `nodelist`: ordered `(hostname, port)` pairs;
- `username` and `password`: URL-decoded strings or `None`;
- `database`: the decoded database name or `None`;
- `collection`: the collection suffix after `database.`, or `None`;
- `options`: a dictionary of normalized option names and converted values;
- `fqdn`: `None` for the supported literal-host `mongodb://` form.

Accept both ampersand and semicolon option separators. Normalize recognized
option names to the driver's canonical spelling. Convert recognized booleans to
`bool`; convert `connectTimeoutMS` milliseconds to seconds as `float` (for
example, `2500` becomes `2.5`). An unsupported scheme raises
`pymongo.errors.InvalidURI`. An out-of-range explicit port raises `ValueError`.

### Scalar Validators

The following functions are imported from `pymongo.common`. Their `option`
argument is used to identify invalid input in the exception message.

- `validate_boolean(option: str, value: Any) -> bool` accepts exactly `True` or
  `False`; other values raise `TypeError`.
- `validate_integer(option: str, value: Any) -> int` accepts integer values;
  non-integers raise `TypeError`.
- `validate_string(option: str, value: Any) -> str` accepts strings;
  non-strings raise `TypeError`.
- `validate_string_or_none(option: str, value: Any) -> str | None` accepts a
  string or `None`; other values raise `TypeError`.
- `validate_is_mapping(option: str, value: Any) -> None` returns `None` for a
  `collections.abc.Mapping` and raises `TypeError` otherwise.

Do not silently coerce rejected values.

## Implementation Notes

Keep imports working both from the source tree and after installation. The
offline verifier runs each behavior in a fresh subprocess against the installed
candidate package, so module globals must not depend on test order. Do not add
test-only modules, inspect verifier files, or hard-code particular scenario
inputs. Implement the public contracts above as normal reusable library code.
