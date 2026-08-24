# SoupSieve

## Authoring Status

This is an evidence-first candidate for SoupSieve. It is pinned to the exact
upstream revision recorded in `task.toml`, but is currently blocked from
benchmark publication until the audit gates in `audit.md` are completed. No
hidden tests, verifier code, Harbor bundle, private artifact, or shared test
asset is part of this candidate.

## Project Description

Create an installable Python package named `soupsieve` that provides CSS
selector matching for BeautifulSoup trees. The package should let callers
select descendants, select one result, stream results, match a tag, find the
closest matching ancestor, filter an iterable of tags, compile reusable
selectors, escape CSS identifiers, and clear selector cache state. Matching
must operate on BeautifulSoup `Tag` and `BeautifulSoup` objects rather than on
a separate DOM implementation.

The implementation target is the behavior of the pinned upstream SoupSieve
revision. Do not copy source code or tests from the upstream repository into
the generated project.

## Supports

- Python 3.12 or another supported Python 3 release.
- `beautifulsoup4` as the runtime integration dependency.
- BeautifulSoup's standard-library `html.parser` lane for examples and local
  checks. Do not require or import `lxml` or `html5lib`.
- Offline installation and execution after the declared dependencies have
  been provisioned. Runtime code must not fetch data from the network.

## API Usage Guide

All selector arguments are text strings. The `tag` argument is a BeautifulSoup
tree or tag. A `namespaces` mapping is optional where shown, `limit=0` means no
result limit, and `flags=0` means default selector parsing behavior.

```python
select(select, tag, namespaces=None, limit=0, flags=0) -> list[Tag]
select_one(select, tag, namespaces=None, flags=0) -> Tag | None
iselect(select, tag, namespaces=None, limit=0, flags=0) -> Iterator[Tag]
match(select, tag, namespaces=None, flags=0) -> bool
closest(select, tag, namespaces=None, flags=0) -> Tag | None
filter(select, iterable, namespaces=None, flags=0) -> list[Tag]
compile(pattern, namespaces=None, flags=0) -> SoupSieve
escape(ident) -> str
purge() -> None
```

`select` returns matching tags in document order and honors a positive result
limit. `select_one` returns the first match or `None`. `iselect` is lazy and
produces the same ordered tags as `select`; it honors the same limit. `match`
checks the supplied tag itself, while `closest` checks that tag and then its
ancestors, returning the nearest match or `None`. `filter` preserves input
order for matching tags. Invalid selector text raises the package's selector
syntax exception instead of silently returning unrelated nodes. Invalid input
types must raise a meaningful exception consistent with the pinned API.

`compile` returns a reusable `SoupSieve` object exposing `select`, `iselect`,
`match`, `closest`, and `filter` with the compiled selector. Compiled objects
retain namespaces and flags independently of later module-level calls.

Support the pinned revision's tag, universal, class, ID, grouped, descendant,
child, adjacent, general-sibling, attribute, namespace, structural, state,
relational, and logical selector behavior. Matching follows BeautifulSoup tree
semantics and must not mutate caller-owned trees.

## Text/JSON Boundary

Selector inputs are text and API results are BeautifulSoup tags. Do not
serialize tags to JSON as a substitute for the Python API, and do not parse a
JSON string where selector text is expected. Any diagnostic text/JSON adapter
must be separate from the public selector functions and must not change their
return types.

```python
from bs4 import BeautifulSoup
import soupsieve

tree = BeautifulSoup('<main><p class="item">One</p><p class="item">Two</p></main>', 'html.parser')
assert [node.get_text() for node in soupsieve.select('p.item', tree)] == ['One', 'Two']
assert soupsieve.select_one('p.item', tree).name == 'p'
assert soupsieve.match('p.item', tree.select_one('p')) is True
```

## Implementation Notes

- Keep public re-exports and exception names consistent with the pinned
  package; private parser helpers are not required API.
- Keep runtime dependencies limited to BeautifulSoup4 and its offline
  transitive closure. `lxml` and `html5lib` are out of scope.
- Do not require network access, remote fixtures, generated caches, or private
