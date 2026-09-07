## Project Description

Create a Python package named `feedparser` that reads a feed supplied by the
caller and exposes the parsed result through the package-level
`feedparser.parse` function. The intended users are applications that consume
RSS, Atom, RDF, or JSON Feed documents without having to write a separate
parser for each feed format. The parser must accept local input only in this
task: bytes, text, or an already-open file-like object. It must not fetch a
remote URL, resolve DNS, contact an HTTP server, read credentials, or depend on
mutable network metadata.

The implementation boundary is deliberately the parser and its observable
result. It includes format detection, character-encoding handling, namespace
and element mapping, date normalization, HTML sanitization, relative-link
resolution when requested, and diagnostic/status information. It does not
include a feed crawler, scheduler, persistence layer, feed editor, database,
GUI, or command-line application. Do not require callers to install or run a
web server. A string that happens to look like a URL is input data unless the
frozen package contract explicitly identifies it as a local path; in all cases,
the implementation must remain safe and deterministic in the no-network
environment.

The source candidate is the `feedparser` project at revision
`a22c5521cbb109871f1a2318948581901bd47e26`, declared BSD-2-Clause in the task
metadata. The detached source archive, dependency lock, and verifier are not
present in this checkout, so the implementation must not invent additional
public APIs, options, or result fields. Keep the public surface compatible with
the package-level parser described below; keep helpers private unless their
names and signatures can be verified from the frozen source before the task is
unblocked.

## Supports

- **Runtime:** Python 3.12.14 on Debian 12 amd64. Use normal Python text and
  bytes semantics and do not require Python 2 compatibility.
- **Package manager and installation:** provide install metadata in
  `pyproject.toml` and make `python -m pip install .` the installation command.
  The harness installs from the workspace, not from a source checkout fetched
  at run time. The declared candidate dependency observations are
  `feedparser-sgmllib`, `requests`, and optional `chardet`; do not silently
  replace them with network-installed packages or add undeclared runtime
  services. The current task descriptor records the offline dependency closure
  as missing, so this source remains blocked until a hash-locked wheel/cache
  bundle is supplied. This instruction does not authorize changing that
  descriptor.
- **Network:** agent, candidate, verifier, Oracle, and controls run with
  `no-network`. They must not access GitHub, PyPI, npm, a Go proxy, DNS,
  numeric IP addresses, loopback HTTP services, or any external service during
  normal parsing. Tests should use in-memory data or files created beneath the
  workspace. A caller-provided opener/handler must not be used to bypass this
  boundary.
- **Import entry point:** `import feedparser` must succeed after installation,
  and `feedparser.parse` must be available from the package root. The package
  name and import name are both `feedparser`; do not expose only a differently
  named module.
- **CLI:** no public command-line entry point is bound by the available source
  evidence. Do not add a CLI requirement or make parser behavior depend on
  `sys.argv`.
- **Harness setup:** the harness invokes the installed package from a clean
  workspace and supplies local bytes, Unicode strings, or file-like objects.
  It may create temporary feed fixtures and change the current working
  directory. The parser must not assume a repository checkout, a home
  directory, a writable global cache, or a particular locale.

### Project Directory Structure

```text
workspace/
├── pyproject.toml
└── feedparser/
    ├── __init__.py          # package root; exports parse
    ├── api.py               # public parser entry point and result assembly
    ├── encoding.py          # input decoding helpers
    ├── parsers.py           # RSS, Atom, RDF, and JSON Feed handling
    ├── sanitization.py      # HTML and text normalization
    └── dates.py             # date conversion helpers
```

The module names below are the minimum suggested organization, not additional
public API promises. If a different internal organization is necessary, keep
the package root and the documented callable unchanged. Do not add a console
script, network client, persistent cache, or generated source tree merely to
fill out the directory listing.

## API Usage Guide

### `feedparser.parse`

**Import path:**

```python
import feedparser
result = feedparser.parse(source)
```

**Callable shape:** the bindable public shape is
`feedparser.parse(source, **kwargs)`. The frozen source archive is not
available in this checkout, so the exact positional name, keyword-only
parameters, defaults, and complete accepted-keyword list cannot be independently
bound here. Commonly supported keyword options in the real feedparser API
include `agent`, `etag`, and `modified`; treat these as optional caller metadata,
not as a complete or frozen signature. Before this blocked task is promoted,
compare every parameter and default with the detached source revision; do not
add parameters based only on a similarly named library.

The first argument accepts one of the supported local input forms:

1. a `bytes` value containing the feed document;
2. a `str` containing feed text; or
3. a readable file-like object whose `read()` returns bytes or text; or
4. a URL string in the upstream API's input domain.

This task's candidate process is nevertheless offline. The harness supplies
local bytes, text, and file-like values, and must not require remote URL
retrieval. If URL-shaped input is accepted for compatibility, it must not cause
DNS or HTTP access in this environment; do not use a network client to make a
local test pass.

The optional HTTP-shaped metadata arguments (`etag`, `modified`, `agent`,
`referrer`, `handlers`, `request_headers`, `response_headers`, and
`response_status`) are metadata supplied by a caller that already obtained the
document. They must not trigger a network request. `resolve_relative_uris`
controls whether relative links are resolved against the document's local base
URI when one is available. `sanitize_html` controls the package's HTML/text
sanitization behavior. `use_datetime` selects the documented date value
representation; preserve one representation consistently for a given option.
Unknown keyword arguments must not silently change the parser or initiate I/O;
match the frozen source's established handling once the source is available.

**Return value and shape:** return a mapping-like `FeedParserDict` parse result.
The stable top-level result contains an ordered `entries` collection and a
feed-level mapping available as `result.feed`; feed and entry mappings expose
their fields through both mapping-style and attribute-style access where the
real package supports it. Parse diagnostics include the public `bozo` flag for
documents that are not fully well-formed, and the result may include
`bozo_exception`, `version`, and response `headers` according to the input and
the frozen package behavior. An entry's standard fields, such as `title`, are
available only when present in the source document. Date fields and other
optional values retain the package's documented representation, including the
`use_datetime` option when that option is supported.

Do not return open file handles, parser nodes, generators, sockets, or arbitrary
custom objects in place of parsed fields. Preserve source order for entries and
repeated child values. Repeated calls with identical input and options must
produce equivalent results and must not mutate a caller-owned byte string, text
string, or file-like object beyond the file object's ordinary read position.

For an ordinary local RSS document:

```python
rss = b'''<?xml version="1.0"?>
<rss version="2.0"><channel>
  <title>Example</title>
  <item><title>First</title><link>/first</link></item>
</channel></rss>'''
parsed = feedparser.parse(rss, resolve_relative_uris=False)
assert parsed.feed.title == "Example"
assert parsed.entries[0].title == "First"
```

For empty input, return the package's normal parse-result mapping with no
entries and diagnostics describing the absence of a usable feed; do not raise
an unrelated `KeyError`, print to stdout, or contact the network:

```python
empty = feedparser.parse(b"")
assert isinstance(empty, dict)
assert empty.entries == []
```

For a readable stream, consume the stream according to the frozen package
behavior and retain the same result contract as bytes input:

```python
from io import BytesIO

stream_result = feedparser.parse(BytesIO(rss))
assert stream_result.entries[0].title == "First"
```

Malformed XML and unsupported feed syntax should follow the real package's
recoverable-result behavior: return a result with `bozo` diagnostics rather
than turning every malformed document into an application crash. An invalid
input object must follow the source-compatible exception behavior. Because the
source archive is absent, the exact exception class, every diagnostic key, and
the complete keyword signature are **not confidently bindable** by this
instruction; do not invent a new exception taxonomy. This is the sole public
callable that can presently be documented with confidence from the available
task evidence.

### Package root exports and non-APIs

`feedparser.__version__` may be provided if it is part of the frozen package's
root exports, but its exact value cannot be bound from the available source and
must not be used as a substitute for parser behavior. No class, helper module,
date-handler registration function, sanitizer class, network opener, or CLI has
been added to this public contract because none can be verified against the
detached revision in the current checkout. Keep such implementation details
private unless the source freeze supplies their exact import path and
signature.

## Implementation Notes

1. **Format boundary.** Recognize the feed families named by the task metadata:
   RSS, Atom, RDF, and JSON Feed. Detection must be based on local content and
   must tolerate an XML declaration, namespaces, BOMs, ordinary Unicode, and
   common byte encodings supported by the frozen package. Do not require the
   caller to pre-select a format.
2. **Result normalization.** Use stable mapping and list values. Keep feed and
   entry order observable, retain repeated values according to the source
   contract, and normalize dates, links, namespaces, and sanitized text without
   exposing native XML nodes. Do not serialize diagnostics by calling `repr()`
   on arbitrary exception or parser objects.
3. **Relative links and HTML.** The two boolean options must be independent:
   disabling relative-link resolution must not disable parsing, and disabling
   sanitization must not cause network access. Sanitization must never execute
   scripts or return executable markup as a side effect.
4. **Determinism and isolation.** Avoid current time, random values, locale,
   environment-dependent ordering, and global mutable registries. Reading a
   file-like input may advance its cursor, but parsing the same bytes twice must
   produce the same JSON-safe structure. All temporary resources must be
   closed or left owned by the caller according to normal file-like semantics.
5. **Compatibility discipline.** Do not copy a source function body or upstream
   tests. The revision, dependencies, full source archive, and separate verifier
   still need to be frozen before this instruction can define a production
   denominator. Until then, treat unbound signatures, result keys, exception
   classes, and extra exports as unresolved rather than guessing them.

Small verifiable examples:

```python
atom = b'''<feed xmlns="http://www.w3.org/2005/Atom">
  <title>News</title><entry><title>One</title></entry>
</feed>'''
atom_result = feedparser.parse(atom)
assert atom_result.feed.title == "News"
assert [entry.title for entry in atom_result.entries] == ["One"]
```

```python
json_feed = b'''{"version":"https://jsonfeed.org/version/1.1",
"title":"Updates","items":[{"id":"1","content_text":"Hello"}]}'''
json_result = feedparser.parse(json_feed)
assert json_result.feed.title == "Updates"
assert json_result.entries[0].id == "1"
```

```python
relative = b'''<rss version="2.0"><channel><title>X</title>
<link>https://example.invalid/base/</link>
<item><link>item</link></item></channel></rss>'''
without_resolution = feedparser.parse(relative, resolve_relative_uris=False)
assert without_resolution.entries[0].link == "item"
```

The examples above are behavior probes, not an algorithm prescription. They
must remain offline and must not depend on `example.invalid` being reachable.
No Oracle, reward, controls, or production-valid status is claimed by this
instruction rewrite; the task remains blocked until the missing source,
dependency, verifier, and evidence artifacts are frozen.
