# Build `tomli`

Create a complete, installable Python distribution named `tomli` from an empty
workspace. It is a small, dependency-free TOML 1.0 parser with a typed import
surface.

## Project Description

The package must use the `src/tomli` layout and expose the `tomli` import
package. The frozen distribution version is `2.4.1`. The evaluator uses
CPython 3.12 and installs the project through its PEP 517 build backend without
network access at test time.

The parser must accept TOML documents supplied as Unicode strings or binary
files and return ordinary Python dictionaries and TOML-native scalar values.
It must reject malformed TOML with a structured `TOMLDecodeError` rather than
silently accepting ambiguous input.

## Supports

- Support Python 3.8 and newer CPython versions.
- Provide a normal PEP 517 project with a build backend available from the
  build environment. Do not require runtime dependencies.
- Keep the implementation local and deterministic. Parsing must not access the
  network, invoke external commands, or rely on the current working directory.
- Include `tomli/py.typed` and make the installed distribution metadata report
  version `2.4.1`.
- Use the `src/tomli` package layout; do not put the implementation in a
  top-level module that only works from the repository root.

## API Usage Guide

### `tomli.loads`

Signature:

```python
tomli.loads(__s: str, *, parse_float: Callable[[str], object] = float) -> dict[str, object]
```

Parse one complete TOML document from a `str`. Return a new dictionary whose
keys are strings. Support comments, bare and quoted keys, dotted keys,
standard tables, arrays of tables, arrays, inline tables, booleans, decimal
integers with binary/octal/hex forms and underscores, decimal floats including
`inf` and `nan`, basic and literal strings, multiline strings, and TOML local
or offset date/time values. Preserve source order where it is observable in a
dictionary and preserve the nesting represented by the document.

The optional `parse_float` callable receives the original textual spelling of
each decimal float and replaces the default `float` conversion. It must not
return a `dict` or `list`; doing so raises `ValueError`. The input must be a
string; non-string input raises `TypeError`.

### `tomli.load`

Signature:

```python
tomli.load(__fp: IO[bytes], *, parse_float: Callable[[str], object] = float) -> dict[str, object]
```

Read a binary file object to completion and parse its UTF-8 contents exactly as
`loads` would. Text-mode file objects are rejected with `TypeError` and the
message explains that the file must be opened in binary mode.

### `tomli.TOMLDecodeError`

`TOMLDecodeError` is a `ValueError` subclass raised for invalid documents. Its
normal constructor is `TOMLDecodeError(msg: str, doc: str, pos: int)`. The
instance exposes the original `msg`, `doc`, and `pos`, plus one-based `lineno`
and `colno`; its string includes the message and the location, or says “end of
document” when the position is at the end. Preserve the documented deprecated
free-form constructor behavior and warning for compatibility.

## Implementation Notes

Keep nested tables and arrays distinct rather than flattening them. Validate
duplicate definitions, invalid keys, invalid escapes, malformed numbers and
invalid dates/times. Handle CRLF input consistently with LF input. Returned
containers should be ordinary mutable Python containers and should be safe to
deep-copy. Keep public exports limited to `loads`, `load`, and
`TOMLDecodeError`, while compatibility with importing `tomli._types` and the
package version metadata must remain intact.
