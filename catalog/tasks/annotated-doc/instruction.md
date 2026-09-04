# Project Description

Create a complete, installable Python project named `annotated-doc` from an
empty workspace. It provides a small runtime object for attaching human-readable
documentation to Python type annotations with `typing.Annotated`.

The scored package surface is intentionally small, but the project must be a
real package rather than a single loose script. The implementation must expose
the documented package metadata, preserve the value supplied by callers, and
work with Python's normal annotation introspection and pickle mechanisms.

# Supports

- Support CPython `>=3.9`.
- Use a `src` layout with the import package at `src/annotated_doc/`.
- Provide an installable `pyproject.toml` using a standard PEP 517 build
  backend. The package has no third-party runtime dependencies.
- Provide `src/annotated_doc/py.typed` so type checkers can treat the package as
  typed.
- Export `Doc` and `__version__` from `annotated_doc`.
- Set the package version to `0.0.5` and keep the distribution metadata and
  runtime `__version__` consistent.
- Do not contact a network, launch a subprocess, or require an external service
  for import or normal object use.
- The repository may include development scripts and tests, but they are not
  part of the runtime API or its dependency set.

# API Usage Guide

## `annotated_doc.Doc`

Import path: `annotated_doc.Doc`

Signature:

```python
class Doc(documentation: str, /) -> None
```

`documentation` is a positional-only text value supplied by the caller. Store
that value in a public instance attribute named `documentation`. Do not add
implicit prefixes, suffixes, whitespace normalization, or formatting markup.

The object is intended to be used as metadata inside `typing.Annotated`:

```python
from typing import Annotated, get_type_hints
from annotated_doc import Doc

def greet(name: Annotated[str, Doc("The person to greet")]) -> None:
    pass

assert get_type_hints(greet, include_extras=True)["name"].__metadata__[0].documentation == (
    "The person to greet"
)
```

`repr(doc)` returns `Doc(<repr of documentation>)`, using Python's ordinary
representation of the stored value. Equal documentation values produce equal
`Doc` objects; different documentation values do not. Comparing a `Doc` with
an object of another type must not make that unrelated object equal to it.

`Doc` objects are hashable. The hash is derived from the documentation value
and equal objects must have equal hashes. Empty strings, Unicode text, quotes,
newlines, and other ordinary string contents are valid values.

The class must remain compatible with Python's standard `pickle` module across
all protocols supported by the running interpreter. Unpickling a `Doc` object
must restore the same observable documentation value and equality behavior.

## Package metadata

`annotated_doc.__version__` is the string `"0.0.5"`, and `annotated_doc.Doc`
is the public class exported by the package root. Importing the root package
must not require callers to import a private module first.

# Implementation Notes

- Keep the public package focused on the documented metadata object. Do not
  require FastAPI, Pydantic, or any other framework at runtime.
- Keep `documentation` public and directly inspectable.
- The positional-only constructor boundary is observable: a second positional
  argument is invalid, while normal keyword arguments must not silently create
  a different constructor contract.
- Preserve ordinary Python object semantics for equality, hashing, repr, and
  pickling. Do not use process-global registries or time-dependent state.
- The hidden verifier uses a separate child process and only checks behavior
  described above. It does not require the upstream repository layout or
  release automation scripts.
