# Project Description

Build `jsonlines`, an installable Python library for reading and writing the
JSON Lines format: one UTF-8 JSON value per physical line. The package is aimed
at streaming use, so readers consume incrementally and writers emit each value
immediately instead of buffering an entire document.

The scored contract is intentionally bounded to the public reader, writer,
file convenience, iteration, JSON conversion, and error behavior below. It
does not require a CLI, networking, dataframe integration, schema validation,
asynchronous I/O, or optional third-party JSON engines.

# Supports

- Python 3.12 on Linux.
- An installable distribution named `jsonlines`, version `4.0.0`.
- The import package `jsonlines`, including a `py.typed` marker.
- `attrs>=19.2.0` as the only required runtime dependency. Standard-library
  modules must not be declared as package-index dependencies.
- A conventional `setup.py`/`setup.cfg` or `pyproject.toml` build that can be
  installed with `pip --no-deps --no-build-isolation` from the repository root.
- No runtime network, subprocess, external-service, or platform-tool behavior.

## Natural Language Instruction

Create the installable `jsonlines` package from an empty workspace. Implement
incremental Reader and Writer wrappers, the file convenience function, JSON
conversion, custom serializer behavior, physical-line numbering, and the
documented exception contract. Preserve stream ownership boundaries: wrappers
created around caller streams must not close those streams, while wrappers
created by `open` own their internally opened file.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── jsonlines/__init__.py
├── jsonlines/py.typed
├── jsonlines/reader.py
├── jsonlines/writer.py
└── jsonlines/cli.py
```

The package root exports only the names specified by `__all__`. Optional CLI
or helper modules must not alter that public list. The implementation is local
and synchronous; no network, subprocess, database, or optional JSON engine is
needed.

The top-level package must export exactly these public names through
`jsonlines.__all__`, in this order:

```python
["Error", "InvalidLineError", "Reader", "Writer", "open"]
```

# API Usage Guide

## Errors

```python
class Error(Exception): ...

class InvalidLineError(Error, ValueError):
    line: str | bytes
    lineno: int
    def __init__(self, message: str, line: str | bytes, lineno: int) -> None: ...
```

`InvalidLineError` is both a library `Error` and a built-in `ValueError`.
Construction removes trailing whitespace from `line`, stores the one-based
`lineno`, and formats the exception message as `"<message> (line <lineno>)"`.
Reader decoding failures must preserve their original `UnicodeDecodeError` or
`ValueError` as `__cause__`.

## `Reader`

```python
Reader(file_or_iterable, *, loads=None)

reader.read(*, type=None, allow_none=False, skip_empty=False)
reader.iter(type=None, allow_none=False, skip_empty=False, skip_invalid=False)
iter(reader)
reader.close()
```

The first argument is either a text/binary readable file object or any iterable
yielding `str` or `bytes` lines. `loads`, when supplied, is called with decoded
text and its return value is used directly. Without `loads`, use normal JSON
decoding. Nested and top-level objects, arrays, strings, numbers, booleans, and
JSON null values inside collections are supported.

`read()` consumes exactly one non-skipped physical line. Binary input is decoded
as strict UTF-8. At most one leading U+001E record-separator or U+FEFF BOM
character is removed from each line before decoding. Consecutive prefix
characters are not all stripped.

- End of input raises `EOFError` with an empty message.
- Invalid UTF-8 raises `InvalidLineError` whose `line` remains the original
  bytes and whose cause is `UnicodeDecodeError`.
- Invalid JSON raises `InvalidLineError` whose `line` is the decoded text and
  whose cause is the decoder's `ValueError`.
- A top-level JSON `null` is invalid by default. With `allow_none=True`, it
  returns Python `None`.
- With `skip_empty=True`, empty or whitespace-only physical lines are consumed
  until a non-empty line or EOF is reached. Without it, an empty line is an
  invalid JSON line.
- `type` may be exactly one of `dict`, `list`, `str`, `int`, `float`, or
  `bool`. Any other value raises `ValueError("invalid type specified")` before
  consuming input. A decoded value that does not have the requested type raises
  `InvalidLineError` with the message prefix
  `line does not match requested type`. A boolean does not satisfy `type=int`.

`iter()` repeatedly delegates to `read()` until EOF. It forwards `type`,
`allow_none`, and `skip_empty`. When `skip_invalid=True`, it consumes and omits
invalid lines; otherwise the first `InvalidLineError` propagates. Direct
iteration is equivalent to `reader.iter()` and returns an iterator, not the
Reader object itself.

`close()` is idempotent. Reads after closing raise
`RuntimeError("reader is closed")`. A Reader used as a context manager closes
itself on exit, but it does not close a file object supplied by the caller.

Example:

```python
reader = jsonlines.Reader(["1\n", "bad\n", "2\n"])
assert list(reader.iter(type=int, skip_invalid=True)) == [1, 2]
```

## `Writer`

```python
Writer(fp, *, compact=False, sort_keys=False, flush=False, dumps=None)

writer.write(obj) -> int
writer.write_all(iterable) -> int
writer.close()
```

`fp` is a text or binary writable file-like object. Each `write(obj)` serializes
one value, writes exactly one `\n` after it, optionally flushes, and returns the
number of characters or bytes written including that newline. The default
serializer uses standard-library JSON behavior with `ensure_ascii=False`:
normal output uses separators `", "` and `": "`; `compact=True` uses `","`
and `":"`; and `sort_keys=True` orders object keys.

`dumps`, when supplied, replaces the default serializer and causes `compact`
and `sort_keys` to be ignored. A custom serializer may return `str` or `bytes`.
The Writer converts text to UTF-8 bytes for a binary stream and decodes UTF-8
bytes for a text stream. It calls the custom serializer once with `{}` during
construction to determine this conversion, then once for each written object.

`write_all(iterable)` writes each object in iteration order and returns the sum
of the individual `write()` results. With `flush=True`, call `fp.flush()` after
every written line.

`close()` is idempotent. Writes after closing raise
`RuntimeError("writer is closed")`. A Writer context manager closes the Writer
but leaves a caller-supplied stream open.

## `open`

```python
open(
    file,
    mode="r",
    *,
    loads=None,
    dumps=None,
    compact=None,
    sort_keys=None,
    flush=None,
) -> Reader | Writer
```

`file` accepts the same path, path-like, bytes-path, or integer file descriptor
forms as built-in `open`. Valid modes are exactly `"r"`, `"w"`, `"a"`, and
`"x"`; any other value raises
`ValueError("'mode' must be either 'r', 'w', 'a', or 'x'")`.

Read mode opens UTF-8 text with initial BOM handling and returns `Reader`.
Write, append, and exclusive-create modes open UTF-8 text and return `Writer`.
Forward `loads` only to a Reader and the writer options only to a Writer. The
returned wrapper owns this internally opened file: closing it, including by
context-manager exit, closes the underlying file. Append preserves existing
data, and exclusive creation propagates `FileExistsError` when the path exists.

# Implementation Notes

- Keep physical line enumeration one-based so errors remain correct after
  skipped or invalid lines.
- Do not use `str.splitlines()`: record-separator handling and newline behavior
  must follow the physical iterable supplied by the caller.
- Reader and Writer representations begin with `<jsonlines.Reader at 0x` or
  `<jsonlines.Writer at 0x` and identify the wrapped object or file path.
- The verifier runs in a separate no-network environment. Trusted expected
  values remain outside the candidate process; candidate code is imported only
  in a bounded unprivileged JSON-lines subprocess.
