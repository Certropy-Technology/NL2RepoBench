# Build `python-multipart`

Create a complete, installable Python project named `python-multipart` from an
empty workspace. The distribution provides the `python_multipart` package and
the compatibility package name `multipart`. It is a streaming parser for URL
encoded, multipart/form-data, and octet-stream request bodies.

## Natural Language Instruction

Create the installable `python-multipart` project from an empty `workspace/`.
Implement the canonical `python_multipart` package and its `multipart`
compatibility import. The project must provide four capability groups: header
and value parsing, stateful field/file lifecycle objects, incremental parsers
for each supported content type, and streaming base64/quoted-printable
decoders. Preserve callback order, split-write behavior, metadata, limits,
exception inheritance, and deterministic byte-oriented results.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── README.md
├── python_multipart/
│   ├── __init__.py
│   ├── multipart.py
│   ├── decoders.py
│   └── exceptions.py
└── multipart/
    └── __init__.py
```

`python_multipart/__init__.py` is the canonical root export and
`multipart/__init__.py` supplies compatibility re-exports. The build metadata
must install both packages. Do not add test, verifier, fixture, cache, or
network-client files to the generated project.

## Project Description

Implement the public behavior of the frozen `python-multipart` API. The parser
must consume bytes incrementally, invoke callbacks in stream order, preserve
field and file metadata, support bounded parsing, and expose deterministic
decoder and header-parsing helpers. The package has no runtime dependencies.

## Supports

- Support CPython 3.10 and newer Python 3.x versions; evaluation uses CPython
  3.12 on Linux.
- Provide a PEP 517 build using a standard build backend and an installable
  project named `python-multipart`.
- Provide both `python_multipart/` and the legacy `multipart/` import package.
  The canonical root is `python_multipart`; the compatibility import must
  expose the same public names and version.
- Use deterministic standard-library behavior only. No network, service,
  database, subprocess, or interactive terminal access is needed at runtime.
- Do not copy upstream tests, fixtures, or source into the generated project.

## API Usage Guide

### Root exports and exceptions

`python_multipart.__version__` is the string `"0.0.32"`. Its `__all__` is an
ordered tuple containing `BaseParser`, `FormParser`, `MultipartParser`,
`OctetStreamParser`, `QuerystringParser`, `create_form_parser`, and
`parse_form`.

Import the exception classes from `python_multipart.exceptions`:
`FormParserError` derives from `ValueError`; `ParseError` derives from
`FormParserError` and accepts `ParseError(message, *, offset=-1)`, retaining
the integer `offset`; `MultipartParseError`, `QuerystringParseError`, and
`DecodeError` derive from `ParseError`; and `FileError` derives from both
`FormParserError` and `OSError`.

### Header and value objects

`parse_options_header(value: str | bytes | None) -> tuple[bytes,
dict[bytes, bytes]]` parses a media type and semicolon-separated parameters.
It accepts text, bytes, or `None`, lowercases the media type and parameter
names, keeps parameter values as bytes, removes surrounding quotes and
backslash escapes, and returns `(b"", {})` for an empty or missing value.
Extended RFC 2231 parameters and continuation fragments are ignored. A plain
parameter takes precedence over an extended spelling.

`Field(name: bytes | None, *, content_type: str | None = None)` buffers a form
field. `write(data: bytes) -> int` and `on_data(data: bytes) -> int` append
bytes; `on_end()`, `finalize()`, and `close()` finish or close it;
`set_none()` changes its value to `None`; and the `field_name`, `value`, and
`content_type` properties return its metadata. `Field.from_value(name, value)`
creates a field with an already-buffered value. Writes return the number of
bytes accepted.

`File` represents an uploaded file. Its accessors are the `field_name`,
`file_name`, `actual_file_name`, `file_object`, `size`, `in_memory`, and
`content_type` properties. `write(data)` and `on_data(data)` append
bytes and return the count. `flush_to_disk()` moves an in-memory upload to a
temporary file while preserving content and metadata. `on_end()`,
`finalize()`, and `close()` finish and release the file. File names are bytes;
the original client name and the sanitized actual name are distinct when a
path is supplied.

### Streaming parsers

`BaseParser()` provides callback management. `callback(name, data=None,
start=None, end=None)` invokes the named callback with the appropriate slice;
`set_callback(name, new_func)` replaces or disables a callback; `close()` and
`finalize()` are lifecycle hooks.

`OctetStreamParser(callbacks: dict = {}, max_size: float = inf)` accepts
`on_start`, `on_data`, and `on_end` callbacks. `write(data: bytes)` forwards
data and returns its length; `finalize()` emits the end callback. It raises
`ValueError` for an invalid negative size and `FileError` when the bounded
maximum is exceeded.

`QuerystringParser(callbacks: dict = {}, max_size: float = inf,
strict_parsing: bool = False)` parses `name=value` pairs separated by `&`.
It accepts arbitrarily split writes, decodes percent escapes and plus signs,
and calls `on_field(field)` for each field. Bare names and empty fields are
handled according to `strict_parsing`; malformed strict input raises
`QuerystringParseError`. `write()` returns the input byte count and
`finalize()` flushes a trailing field.

`MultipartParser(boundary: bytes, callbacks: dict = {}, max_size: float = inf,
max_header_size: int = 64 * 1024, max_header_count: int = 8)` parses a
multipart body incrementally. It emits the documented part/header/data/end
callbacks, preserves part order, accepts preamble and epilogue, decodes
`Content-Transfer-Encoding: base64` and `quoted-printable`, and raises
`MultipartParseError` or `FileError` for malformed input or size limits.

`FormParser(content_type: str, on_field: Callable | None, on_file: Callable |
None, boundary: bytes | None = None, config: dict = {})` selects the proper
streaming parser for `application/x-www-form-urlencoded`,
`multipart/form-data`, or `application/octet-stream`. `write(data)`,
`finalize()`, and `close()` delegate to the selected parser. File callbacks
receive `File` objects and field callbacks receive `Field` objects.

`create_form_parser(headers: dict[str, bytes], on_field, on_file,
config={}) -> FormParser` reads the content type and boundary from headers and
constructs a form parser. `parse_form(headers, input_stream, on_field,
on_file) -> None` reads a file-like object in bounded chunks, parses it, and
delivers callbacks. Invalid content types, missing boundaries, malformed
content length, and invalid chunk sizes must raise the package's documented
parser exceptions rather than silently accepting the request.

### Streaming decoders

`Base64Decoder(underlying)` and `QuotedPrintableDecoder(underlying)` adapt a
file-like object with `write(bytes)`. Their `write()` methods return the input
length and may cache an incomplete final sequence across calls. `finalize()`
flushes the cache or raises `DecodeError` for incomplete base64; `close()`
forwards to the underlying object when supported. Base64 decode failures are
reported as `DecodeError`.

## Implementation Notes

- Preserve observable return types, callback order, incremental behavior,
  exception inheritance, metadata accessors, and deterministic representations.
- Keep candidate code under the workspace and make the project installable
  without downloading anything during evaluation. The evaluator installs only
  the project itself; it does not run upstream tests.
- Use bounded temporary-file behavior for uploads. Do not require a network,
  database, native extension, external service, or environment-specific path.
- The hidden verifier calls the public API through an isolated child process;
  do not rely on trusted verifier imports or files.

## Examples

```python
from python_multipart.multipart import parse_options_header

media_type, options = parse_options_header(
    'multipart/form-data; boundary="abc"'
)
```

```python
from python_multipart.multipart import QuerystringParser

fields = []
parser = QuerystringParser({"on_field": fields.append})
parser.write(b"name=one&name=two")
parser.finalize()
```

```python
from io import BytesIO
from python_multipart.decoders import Base64Decoder

decoded = BytesIO()
decoder = Base64Decoder(decoded)
decoder.write(b"aGk=")
decoder.finalize()
```

## Error Handling and Boundary Conditions

- Parser writes may split at any byte boundary; callbacks remain in input order
  and `write()` reports the number of accepted input bytes.
- Invalid content types, missing multipart boundaries, malformed headers,
  malformed encodings, and exceeded `max_size` limits raise the documented
  parser or decoder exception instead of being silently accepted.
- `Field` and `File` lifecycle methods are deterministic and idempotent where
  documented; closing a temporary upload releases its file resource.
- Empty query fields, bare names, quoted header parameters, and a trailing
  partial decoder sequence follow the strictness and error contracts above.
