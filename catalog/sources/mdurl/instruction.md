# Build `mdurl`

Create a complete, installable Python distribution named `mdurl` from an empty
workspace. It is a small, deterministic Markdown URL utility library and must
work without network, filesystem, subprocess, or service behavior at runtime.

## Project Description

The package provides the URL parsing and percent-encoding behavior needed by
Markdown tooling. It separates a URL into protocol, slashes, authentication,
port, hostname, fragment, query, and pathname components, and can format that
structured value back to text. It also encodes unsafe text while preserving
already-valid escapes and decodes percent-encoded UTF-8 with replacement
characters for malformed sequences.

## Supports

- Support CPython 3.10 and newer Python 3.x versions in the package metadata;
  the evaluation runtime is CPython 3.12.
- Use a PEP 517 build with `flit_core` and produce an importable `mdurl`
  package containing a `py.typed` marker. There are no runtime dependencies.
- Expose the public names and constant values listed below from `mdurl`.
- Keep all operations deterministic and local. Do not use the network or rely
  on the current working directory, current time, locale, or random state.

## API Usage Guide

### Root exports

`mdurl.__version__` is the string `"0.1.2"`. The root module's `__all__` is a
tuple in this order:

```text
decode, DECODE_DEFAULT_CHARS, DECODE_COMPONENT_CHARS, encode,
ENCODE_DEFAULT_CHARS, ENCODE_COMPONENT_CHARS, format, parse, URL
```

The root module re-exports `decode`, `encode`, `format`, `parse`, `URL`, and the
four character-set constants. `URL` is an immutable named-tuple-like type with
fields, in order, `protocol`, `slashes`, `auth`, `port`, `hostname`, `hash`,
`search`, and `pathname`. It supports indexing, unpacking, equality, and
attribute access.

### `parse`

Import path: `from mdurl import parse`

Signature: `parse(url: str | URL, *, slashes_denote_host: bool = False) -> URL`

For a `URL` input, return the same object. For text input, return a `URL` with
each component either a string, `True` for `slashes`, or `None` when absent.
Trim surrounding whitespace before parsing. Recognize a leading protocol using
letters, digits, `.`, `+`, and `-`, preserving its original case and trailing
colon. For `http`, `https`, `ftp`, `gopher`, and `file`, a host is expected
when the input has the relevant slash form; other protocols may also have a
host when `//` or protocol syntax indicates one. Preserve the distinction
between a missing pathname (`None`) and an explicitly empty pathname (`""`)
for a slashed host URL.

Split an authority into the last applicable `@` authentication section,
hostname, and a numeric trailing port. IPv6 host brackets are accepted and
removed from the stored `hostname`; `format` restores them. The hostname is
limited to 255 characters and stops at URL host delimiters. Preserve Unicode
and literal characters in components; do not URL-decode them. `?` begins the
search component and `#` begins the hash component, with the hash split first.

The `slashes_denote_host=True` keyword changes relative `//...` inputs to use
the authority parsing rules. The parser is intentionally compatible with the
Node-style URL behavior used by Markdown tooling, including unusual but valid
relative paths, custom protocols, user information, empty numeric ports,
Unicode host text, IPv6, and delimiter characters.

### `format`

Import path: `from mdurl import format`

Signature: `format(url: URL) -> str`

Reassemble the eight URL fields in their stored order: protocol, `//` when
`slashes` is true, `auth@`, bracketed IPv6 hostname, `:port`, pathname,
search, and hash. Treat falsey or missing optional fields as absent. This is a
pure operation and must preserve the parser's observable round-trip behavior,
including unusual characters and empty components.

### `encode`

Import path: `from mdurl import encode`

Signature: `encode(string: str, exclude: str = ENCODE_DEFAULT_CHARS, *, keep_escaped: bool = True) -> str`

Percent-encode characters not in ASCII letters, digits, or `exclude`. The
default `ENCODE_DEFAULT_CHARS` is `";/?:@&=+$,-_.!~*'()#"` and
`ENCODE_COMPONENT_CHARS` is `"-_.!~*'()"`. ASCII hex digits in generated
escapes are uppercase. With `keep_escaped=True`, preserve an existing `%` plus
two hexadecimal digits exactly; with false, encode every percent sign. Non-ASCII
text is UTF-8 percent-encoded. Unpaired UTF-16 surrogate characters become
the UTF-8 replacement sequence `%EF%BF%BD`; a valid surrogate pair is encoded
as its Unicode code point. Characters in `exclude` remain literal, including
when they would otherwise be encoded. The function returns a string and does
not mutate input or global observable state.

### `decode`

Import path: `from mdurl import decode`

Signature: `decode(string: str, exclude: str = DECODE_DEFAULT_CHARS) -> str`

Decode contiguous valid `%XX` bytes. The default `DECODE_DEFAULT_CHARS` is
`";/?:@&=+$,#"` and `DECODE_COMPONENT_CHARS` is the empty string. Characters
listed in `exclude` remain percent-escaped, while other ASCII bytes decode to
their characters. Valid multi-byte UTF-8 sequences decode to Unicode. Invalid
or incomplete UTF-8 sequences use U+FFFD replacement characters while the
surrounding text and malformed non-hex escapes remain unchanged. The function
is deterministic and returns a new string.

## Implementation Notes

- Keep package code split into focused modules if useful, but preserve the
  root imports, constants, signatures, named-tuple field order, and version.
- Parsing and formatting are intentionally not the same as
  `urllib.parse.urlparse`; implement the documented Node-style edge behavior.
- Do not copy the upstream source, tests, README, or fixture data into the
  workspace. Hidden checks invoke the public API in an isolated unprivileged
  child process and use no network.
