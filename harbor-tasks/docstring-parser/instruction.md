# Build `docstring_parser`

Create a complete, installable Python project from an empty workspace. The
distribution name and import package are both `docstring_parser`, and the
package version is `0.18.0`. Implement the project as a normal package from
the standard library; do not wrap an already-installed copy of the library.

## Supports

- Support Python 3.8 and newer.
- `pip install .` works without network access when build requirements are
  already available in the environment.
- Normal imports have no runtime dependency outside the Python standard
  library.
- Preserve Unicode text, indentation, and meaningful line breaks.
- Include packaging metadata and a concise README with an installation and
  usage example.

The frozen evaluation uses a deterministic JSON-safe slice of the public API.
It does not require a command-line interface, network access, or external
services. The adapter invokes the normal Python APIs in a child process; do
not add an adapter-specific public entry point.

## Public API Slice

The package root exports these names:

```python
from docstring_parser import (
    parse,
    compose,
    ParseError,
    Docstring,
    DocstringMeta,
    DocstringParam,
    DocstringRaises,
    DocstringReturns,
    DocstringDeprecated,
    DocstringStyle,
    RenderingStyle,
    Style,
)
```

`Style` is the backwards-compatible alias for `DocstringStyle`. The defining
module `docstring_parser.common` exposes the same model and enum classes.
`DocstringStyle` has `REST`, `GOOGLE`, `NUMPYDOC`, `EPYDOC`, and `AUTO`;
`RenderingStyle` has `COMPACT`, `CLEAN`, and `EXPANDED`. `ParseError` is a
`RuntimeError` subclass for malformed metadata in an explicitly selected
dialect.

`Docstring` contains `short_description`, `long_description`,
`blank_after_short_description`, `blank_after_long_description`, `meta`, and
`style`. Its `description` property joins the descriptions, and its `params`,
`raises`, `returns`, and `many_returns` properties filter metadata while
preserving source order. `DocstringParam` exposes `arg_name`, `type_name`,
`is_optional`, and `default`. `DocstringReturns` exposes `type_name`,
`is_generator`, and `return_name`. `DocstringRaises` exposes `type_name`.

## Parsing

Implement:

```python
parse(text: str | None, style: DocstringStyle = DocstringStyle.AUTO) -> Docstring
```

`None` and the empty string return an empty document. Clean normal Python
docstring indentation. An explicit style selects only that dialect and sets
the returned `Docstring.style`. `AUTO` chooses deterministically among the
four dialects, preferring the interpretation with the most structured
metadata and breaking ties in the order ReST, Google, Numpydoc, Epydoc.

The frozen slice checks these dialect behaviors:

- ReST fields use `:param`, `:type`, `:returns`, `:rtype`, `:raises`, and
  generic `:name args:` forms. A typed parameter can be optional with `?`;
  descriptions containing `defaults to VALUE` expose `default`.
- Google headings include `Args:`, `Returns:`, and `Yields:`. Parameters use
  `name (type): description`; `optional` and `?` mark optional parameters.
  `. Defaults to VALUE.` exposes a default. Simple PEP 604 unions such as
  `bytes | memoryview` are return or yield type declarations.
- Numpydoc uses an underlined `Parameters` or `Returns` heading. Parameter
  types may end with `, optional`, and indented descriptions are preserved.
  `Raises` entries expose their exception type.
- Epydoc combines `@param` with `@type`, and `@return` with `@rtype`;
  `@raise ExceptionType:` exposes a typed raise.

Unknown ReST fields remain `DocstringMeta` with their field words in `args`.
Malformed explicitly selected fields raise `ParseError`.

## Composition

Implement:

```python
compose(
    docstring: Docstring,
    style: DocstringStyle = DocstringStyle.AUTO,
    rendering_style: RenderingStyle = RenderingStyle.COMPACT,
    indent: str = "    ",
) -> str
```

`AUTO` uses `docstring.style`; an explicit style uses that dialect. Preserve
description text, metadata order, type and optional information, generator
versus return information, and blank-description flags. Output is stable and
has no trailing blank line. `COMPACT`, `CLEAN`, and `EXPANDED` control whether
metadata descriptions stay on their header line or use indented continuation
lines. `indent` controls continuation and item indentation.

The dialect modules `docstring_parser.rest`, `google`, `numpydoc`, and
`epydoc` also expose `parse(text)` and `compose(docstring,
rendering_style=..., indent=...)` with the same behavior for their notation.

## Example

```python
from docstring_parser import DocstringStyle, parse

doc = parse(
    """
    Brief summary.

    Args:
        count (int): number of records
    """,
    style=DocstringStyle.GOOGLE,
)
assert doc.params[0].arg_name == "count"
```
