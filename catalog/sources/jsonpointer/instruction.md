# Project Description

Create a complete, installable Python distribution named `jsonpointer` from an
empty workspace. The library identifies nodes in JSON-like documents using the
JSON Pointer syntax from RFC 6901. The scored contract is the public API below;
do not depend on an upstream checkout, a preinstalled `jsonpointer`, or runtime
network access.

# Natural Language Instruction

From an empty workspace, implement RFC 6901 JSON Pointer resolution and
mutation as the installable `jsonpointer` package. Preserve pointer escaping,
mapping and sequence traversal, append markers, immutable-copy mode, duck-typed
getitem behavior, comparison/representation, and the documented exception
types. The package has no CLI requirement beyond the optional entry point.

# Supports or Environment Configuration

- Python 3.12 on Linux, with an installable distribution and import module both
  named `jsonpointer`.
- Version `3.1.1`, exposed as `jsonpointer.__version__`.
- A conventional `setup.py`/`setup.cfg` or `pyproject.toml` build installable
  from the repository root with `pip --no-deps --no-build-isolation`.
- No third-party runtime dependencies. Standard-library modules are sufficient.
- The optional `bin/jsonpointer` console script may be provided, but the scored
  API is the importable module.

# Project Directory Structure

```text
workspace/
├── setup.py
├── setup.cfg
├── README.md
└── jsonpointer/
    ├── __init__.py
    └── py.typed
```

# API Usage Guide

### Module functions

```python
set_pointer(doc, pointer, value, inplace=True) -> object
resolve_pointer(doc, pointer, default=_nothing) -> object
pairwise(iterable) -> iterator
escape(s: str) -> str
unescape(s: str) -> str
```

`resolve_pointer` accepts a pointer string, resolves it from the document, and
returns the root for the empty pointer. Pointer paths start with `/`; each
component is separated by `/`. Decode `~1` to `/` and `~0` to `~`, in that
order. Other characters, including percent signs and spaces, are literal and
must not be URL-decoded. Mapping components are string keys; sequence
components are non-negative decimal indices without leading zeroes, except
`-`, which represents the position immediately after the last list item.

Missing members, invalid indices, out-of-bounds indices, an invalid starting
form, and invalid escape sequences raise `JsonPointerException`. A supplied
`default` is returned for resolution failures; without one the exception is
raised. Resolving `-` on a list returns an `EndOfList` marker, while trying to
walk beyond that marker raises `JsonPointerException`.

`set_pointer` replaces the selected value and returns the resulting document.
With `inplace=True` it mutates the supplied document; with `inplace=False` it
deep-copies the document before changing it. The empty pointer replaces the
whole document only when `inplace=False`; setting the final `-` component on a
sequence appends a value. Intermediate mappings must already exist, while a
missing final mapping member may be created.

`pairwise` lazily yields adjacent pairs: an empty or one-item input yields no
pairs, and `[1, 2, 3]` yields `(1, 2)` and `(2, 3)`. `escape` replaces `~`
with `~0` and `/` with `~1`; `unescape` reverses those two JSON Pointer escape
sequences.

### `JsonPointer`

```python
class JsonPointer(pointer)
JsonPointer.resolve(doc, default=_nothing)
JsonPointer.get(doc, default=_nothing)
JsonPointer.set(doc, value, inplace=True)
JsonPointer.to_last(doc) -> tuple[object, object | None]
JsonPointer.get_part(doc, part) -> str | int
JsonPointer.get_parts() -> list[str]
JsonPointer.contains(ptr) -> bool
JsonPointer.join(suffix) -> JsonPointer
JsonPointer.from_parts(parts) -> JsonPointer
```

Construction validates the leading slash and escape sequences and stores
unescaped string components in `parts`. `get_parts()` returns those components
in order. `path` is a property containing the escaped canonical pointer string;
`str(pointer)` equals it and `repr(pointer)` has the form
`JsonPointer('<escaped path>')`. Pointers compare equal when their components
are equal, compare unequal to other types, and are hashable consistently with
that equality. `from_parts` accepts unescaped parts, stringifies them, and
returns a pointer. `join` accepts another pointer, a pointer string, or an
iterable of unescaped parts and appends it; `/` is an alias for `join`.

`contains` is true when the argument's components are a prefix of the pointer's
components, including a pointer containing itself. `to_last` resolves all but
the final component and returns `(parent, final_part)`; for the root pointer it
returns `(doc, None)`. `get_part` returns a mapping key, a validated integer
sequence index, or `-` for the append position. Objects that implement
`__getitem__` are supported by duck typing. `EndOfList(list_)` is the marker
returned for the `-` position and its representation identifies the list.

`JsonPointerException` is the library exception type, and `EndOfList` is the
public marker class. The module's existing public classes and functions must
remain importable with these names.

# Implementation Notes

- Keep pointer component order deterministic and preserve Unicode and literal
  characters exactly.
- Do not URL-decode pointer strings and do not accept leading-zero sequence
  indices, signs, decimals, or whitespace as indices.
- Preserve caller documents for `inplace=False`; nested list append and mapping
  assignment must obey the selected mutation mode.
- The verifier imports candidate code only in a bounded unprivileged child
  process. Trusted expected values and test logic are outside the candidate
  workspace, and the verifier runs with no network.

# Examples

```python
from jsonpointer import resolve_pointer, set_pointer

doc = {"a": [1, 2]}
assert resolve_pointer(doc, "/a/1") == 2
set_pointer(doc, "/a/-", 3)
```

```python
from jsonpointer import JsonPointer

pointer = JsonPointer.from_parts(["a/b", "~key"])
assert pointer.path == "/a~1b/~0key"
```

# Error Handling and Boundary Conditions

- Invalid leading forms, malformed escapes, missing mapping members, invalid
  indexes, leading-zero indexes, and out-of-range indexes raise
  `JsonPointerException` unless a default is supplied for resolution.
- `-` is valid only as the final sequence append marker; walking beyond it is
  an error.
- `inplace=False` must not mutate the caller's document, and pointers are not
  URL-decoded.
