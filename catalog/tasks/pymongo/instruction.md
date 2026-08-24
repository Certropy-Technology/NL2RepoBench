# Project Description

Build an installable Python repository that provides the deterministic parts of
the PyMongo/BSON public API described below. The package is evaluated without a
MongoDB server, so this task covers document serialization, ObjectId
validation, MongoDB URI parsing, and scalar option validation. Do not require a
running database or a network connection at runtime.

The repository must install with `python -m pip install .` and expose the
`bson` and `pymongo` import packages. Preserve the public import paths and
return shapes. A compiled extension is optional; behavior is the contract.

## Supports

- Python 3.12 on Linux.
- A standard PEP 517 build using `pyproject.toml`.
- Runtime dependencies must be declared by the project and must not be
  fetched by the test runner.
- The package version must be `4.18.0.dev0`.
- No MongoDB server, DNS query, external service, or network access is needed
  for the supported API.

## API Usage Guide

### `pymongo.__version__`

Expose the string `"4.18.0.dev0"`.

### `bson.json_util.dumps` and `bson.json_util.loads`

`dumps(value)` returns a JSON string using the standard JSON spelling for
objects, arrays, strings, booleans, and null. It uses compact JSON separators
compatible with Python's default `json.dumps` output, sorts object keys, and
escapes non-ASCII characters by default.

`loads(text)` accepts a JSON string (including surrounding whitespace) and
returns the corresponding Python dictionaries, lists, strings, numbers,
booleans, and `None`. Invalid JSON raises the underlying JSON decoding
exception rather than returning a partial result.

### `bson.objectid.ObjectId.is_valid`

`ObjectId.is_valid(value)` returns a boolean. In this deterministic slice it is
true for a 24-character hexadecimal string and false for malformed values,
including a 12-character text string, integers, and `None`. The method must
be available at the documented class import path.

### `pymongo.uri_parser.parse_host`

`parse_host(host)` returns a two-item tuple `(hostname, port)`. Hostname
matching is case-insensitive and the returned hostname is lowercase. An
explicit port is an integer from 1 through 65535; an omitted port defaults to
27017. Bracketed IPv6 literals are accepted and returned without brackets.
Invalid port ranges raise `ValueError`.

### `pymongo.uri_parser.split_hosts`

`split_hosts(hosts)` parses a comma-separated host list into a list of
`(hostname, port)` tuples using the `parse_host` rules. An omitted port uses
27017. Empty host entries raise `pymongo.errors.ConfigurationError`.

### `pymongo.uri_parser.parse_uri`

`parse_uri(uri)` accepts `mongodb://` URIs with optional URL-encoded user
credentials, database name, collection name, and semicolon or ampersand
separated options. Option names are normalized to the driver's canonical
spelling and recognized boolean and numeric values are converted to Python
booleans or numbers. It returns a mapping with exactly these keys:
`nodelist`, `username`, `password`, `database`, `collection`, `options`, and
`fqdn`. `nodelist` is a list of `(hostname, port)` tuples; absent values are
represented by `None`, an empty options mapping, or an empty collection as
appropriate. User information is URL-decoded. An unsupported scheme raises
`pymongo.errors.InvalidURI`, and an invalid port raises `ValueError`.

### Scalar validators in `pymongo.common`

- `validate_boolean(option, value)` returns the boolean when `value` is
  exactly `True` or `False`; otherwise it raises `TypeError`.
- `validate_integer(option, value)` returns an integer value and rejects
  non-integer values with `TypeError`.
- `validate_string(option, value)` returns a string and rejects non-strings
  with `TypeError`.
- `validate_string_or_none(option, value)` returns a string or `None` and
  rejects other values with `TypeError`.
- `validate_is_mapping(option, value)` returns `None` for a mapping and raises
  `TypeError` for a non-mapping.

Exception messages should identify the offending option or value sufficiently
for a caller to diagnose the input. Do not silently coerce invalid values.

## Implementation Notes

Keep the package layout conventional so imports work both from a source tree
and after installation. The supported behavior is intentionally local and
deterministic; database client methods, authentication, encryption, GridFS,
server discovery, and other network-backed features are outside this task.
Do not add test-only modules or hard-code the verifier's test data.
