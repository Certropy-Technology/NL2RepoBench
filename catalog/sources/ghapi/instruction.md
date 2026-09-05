# Build `ghapi`

Create an installable Python package named `ghapi`, version `2.1.3`, from an
empty workspace. This task focuses on the deterministic, local utility surface
of the pinned `fastai/ghapi` release; it must not contact GitHub or any other
network service during evaluation.

## Project Description

`ghapi` is a Python client toolkit for GitHub. Its public helpers include
date conversion, dependency-graph planning, RFC 5988 pagination parsing,
pagination iterators, and issue-template rendering. Implement these helpers as
an installable package while preserving the package's module layout and the
documented behavior below.

## Supports

- CPython 3.12 on Debian 12 amd64 with the pinned build-time dependency
  closure (`fastcore`, `fastspec`, and `fasttransport` plus their locked
  transitive dependencies).
- `pip install .` and editable installation from a clean workspace.
- Package files `ghapi/__init__.py`, `ghapi/core.py`, `ghapi/page.py`,
  `ghapi/auth.py`, `ghapi/all.py`, and `ghapi/py.typed`.
- No runtime network, subprocess, browser, GitHub token, environment download,
  or source checkout behavior is required by the scored contract.

## Natural Language Instruction

Build the installable `ghapi` Python distribution from an empty workspace.
Implement every public module and symbol listed in the API guide, preserving
date conversion, dependency-graph, pagination, issue-template, and auth helper
contracts while keeping deterministic local behavior.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
└── ghapi/
    ├── __init__.py
    ├── core.py
    ├── page.py
    ├── auth.py
    └── all.py
```

The import paths and root re-exports must match the API guide. Do not create
private verifier, hidden-test, or source-archive files in this project.

## Examples

```python
from ghapi.core import date2gh, gh2date
encoded = date2gh(datetime(2024, 1, 2, tzinfo=timezone.utc))
decoded = gh2date(encoded)
```

```python
from ghapi.page import parse_link_hdr
parse_link_hdr('')
```

## Error Handling and Boundary Conditions

Keep timezone, malformed-header, empty-input, dependency-cycle, and missing
optional-value behavior as specified in the API guide. All outputs must be
deterministic and local; no GitHub request or credential lookup is allowed.

## API Usage Guide

### `ghapi.core.date2gh(dt: datetime) -> str`

Return an ISO timestamp suitable for GitHub. Remove microseconds and append
`Z` to the result of `dt.isoformat()`. The input is treated as a UTC datetime;
the upstream behavior preserves an explicit UTC offset in the ISO text before
the final `Z`.

### `ghapi.core.gh2date(dtstr: str) -> datetime`

Parse a GitHub timestamp into a `datetime`. A trailing `Z` is removed before
calling the standard ISO parser, so the returned UTC value is naive for the
usual `...Z` input.

### Dependency graph helpers

- `dep_key(dep: str) -> str` strips an environment marker, version/operator
  clause, and extras from a PEP 508-style dependency, then case-folds the
  package name. Whitespace around the dependency is ignored.
- `local_dep_graph(root) -> dict[str, tuple[str, list[str]]]` scans direct
  child directories containing `pyproject.toml`, and returns package-name keys
  mapped to `(directory_name, dependency_keys)`. Ignore children without a
  project name and keep results deterministic.
- `dep_closure(name, graph) -> set[str]` returns repository directory names for
  the named package and all transitive dependencies present in `graph`.
- `dep_order(graph, names=None) -> list[str]` returns the requested package or
  repository names in dependency-first order. Ties are deterministic and
  prefer packages depended on by more requested packages. Raise `ValueError`
  when a dependency cycle prevents a complete order.
- `dep_dependents(graph, names=None) -> dict[str, list[str]]` returns, for each
  requested item, the requested items that transitively depend on it. Sort the
  mapping by decreasing dependent count with deterministic ties.

### `ghapi.page.parse_link_hdr(header: str) -> dict[str, tuple[str, dict]]`

Parse an RFC 5988 `Link` header. Map each `rel` attribute to `(url, attrs)`;
preserve token and quoted attribute values, convert a bare attribute to
`None`, and raise an exception for malformed trailing input.

### Pagination helpers

- `async paged(oper, *args, per_page=30, max_pages=9999, **kwargs)` yields each
  non-empty page from an async operation, requesting pages `1..max_pages` and
  stopping at the first empty page.
- `async pages(oper, n_pages, *args, per_page=100, **kwargs)` returns a list-like
  result containing exactly the requested pages, fetched concurrently.
- `sync_paged(oper, *args, per_page=30, max_pages=9999, **kwargs)` is the
  synchronous equivalent of `paged`.

### `ghapi.core.issue_body(tmpl, sections) -> str`

Render a form-style issue template. `tmpl.sections` is ordered and each section
has `label`, `type`, `required`, and optionally `options`. Require all required
sections, reject unknown section labels, and emit `### <label>` blocks in
template order. For a `checkboxes` section, `True` checks every option and an
iterable checks only listed option labels. A markdown template represented by
`tmpl.raw` must raise `ValueError` telling the caller to adapt the raw text.

### Small public containers and auth helper

`GhRows` is a list-like container whose representation is one `repr(item)` per
line. `Scope` contains the documented GitHub scope names and
`scope_str(*scopes)` joins non-empty values with commas. `ghapi.__version__`
must be `"2.1.3"`; `ghapi.all` re-exports the scored helpers.

## Implementation Notes

Keep all ordering deterministic and preserve normal Python exception types and
messages where specified. The verifier invokes the candidate through a
separate UID-isolated subprocess and passes only JSON-compatible scenarios;
do not add network fallbacks or read hidden files. The full upstream generated
GitHub endpoint surface is outside this bounded local contract, but module
imports must remain safe when no token or network is available.
