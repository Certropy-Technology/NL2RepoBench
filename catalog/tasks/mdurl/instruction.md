# Build `mdurl`

## Project Description

Create the `mdurl` project from an empty workspace. This is a repository-generation task for the frozen `python` package contract, task specification version `1.0.0`, at source revision `524d2edbbcb8bb48301ba716c7482827bcabb281`. Implement the public behavior described by the local inventories and the task-specific detail below; do not copy upstream source or tests. The supported scope is python, url, parsing, percent-encoding, commonmark, separate-verifier.

## Natural Language Instruction

Starting with an empty `workspace/`, create an installable `mdurl` project. Implement every public/core API named in the API Usage Guide, its package exports, and its documented integration points. Preserve observable input types, return shapes, ordering, determinism, state changes, and documented exception behavior. The project must be usable through its declared `mdurl` import path (or the package root for this Node task), and all required modules must be present in the directory structure below.

The task-specific specification retained below supplies the detailed behavior for each API family. Treat it as the contract: do not add unrelated APIs, replace deterministic behavior with randomized or time-dependent behavior, or weaken error handling.

## Supports

- Language/runtime: `python` on `3.12.14`; target environment metadata declares `debian-12-amd64`.
- Distribution/package: `mdurl`; import/root name: `mdurl`. Package manager: `pip`.
- Install from the repository root with `python -m pip install . --no-deps`. Build metadata must be complete and agree with the package entry point.
- Dependency status in the frozen source metadata is `known`. Use only dependencies declared by the task and available in the preinstalled build image; standard-library modules are not third-party runtime dependencies.
- NoNetwork boundary: agent, candidate, verifier, Oracle, and controls run with `network_mode=no-network`. Do not access GitHub, PyPI, npm registries, Go proxy, DNS, or external services at runtime. Do not fetch source or dependencies during implementation or package use.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── mdurl/
│   └── __init__.py
└── README.md
```

The tree is the minimum public project layout. Add a module only when it corresponds to a documented import path or package resource. Do not place publicly unavailable evaluator code, non-public evaluation material, Oracle payloads, dependency caches, or trusted reports in this workspace.

## API Usage Guide

The public/core API families recorded in the local inventory are: Root exports, `parse`, `format`, `encode`, `decode`.

For each listed family, the detailed contract below defines the import path or CLI entry, signature, accepted inputs, return type/shape, ordering and determinism, state or I/O side effects, errors, and examples. Implement the complete public surface, including root re-exports and aliases where the specification names them. If an API is stateful, preserve mutation and repeated-call behavior; if it is pure, do not introduce global state.

## Implementation Notes

Keep the implementation self-contained and deterministic under the declared runtime. The candidate repository must install from the workspace root, import through the documented public path, and run without external services. Preserve package metadata, module semantics (ESM/CommonJS or Python import behavior), serialization formats, resource cleanup, and boundary behavior described below. publicly unavailable evaluator adapters and non-public evaluation details are not part of the implementation.

## Examples

Ordinary project examples:

```bash
cd workspace
python -m pip install . --no-deps
```

```python
# Import the public package and use the task-specific APIs documented below.
from mdurl import *
```

The retained task-specific examples below provide ordinary API calls and combinations grounded in the frozen inventory. Keep their result shapes and ordering exact.

## Error Handling and Boundary Conditions

- Empty inputs, malformed values, missing resources, duplicate values, and unsupported options must follow the task-specific error contracts below; do not silently coerce or discard information unless explicitly specified.
- Repeated calls must remain deterministic. Filesystem, process, clock, random, native, callback, and serialization boundaries are supported only where the local specification documents them.
- Network attempts are prohibited and must not be used as a fallback. Installation failures, missing offline dependencies, or unsupported external capabilities are environment/source concerns, not reasons to invent behavior.


## Source-derived task detail

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
