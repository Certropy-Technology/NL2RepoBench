# Build `docstring_parser`

Create a complete, installable Python project from an empty workspace. The
distribution name and import package must both be `docstring_parser`. The
package parses docstrings written in ReST, Google, Numpydoc, and Epydoc
notation into a common object model, and can compose that model back into a
selected notation.

The implementation must be a normal Python package, not a collection of test
fixtures or a wrapper around an installed copy of this project. Include
packaging metadata, a concise README with installation and usage examples, and
the public import paths described below.

## Supports

- Support Python 3.8 and newer.
- Runtime behavior must use only the Python standard library. `pytest` is a
  test-only dependency and must not be required by a normal import.
- `pip install .` must install the package and expose package metadata version
  `0.18.0`.
- There is no command-line interface requirement.
- Preserve text content, Unicode characters, indentation, and line breaks as
  described below. Do not require network access or external services at
  runtime.

## Public API

The top-level package must export these names from `docstring_parser`:

```python
from docstring_parser import (
    parse,
    parse_from_object,
    combine_docstrings,
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

`Style` is a backwards-compatible alias for `DocstringStyle`.

The defining module paths used by the package are public too:

```python
from docstring_parser.common import (
    ParseError,
    Docstring,
    DocstringMeta,
    DocstringParam,
    DocstringRaises,
    DocstringReturns,
    DocstringDeprecated,
    DocstringExample,
    DocstringStyle,
    RenderingStyle,
)
from docstring_parser.parser import parse, parse_from_object, compose
from docstring_parser.util import combine_docstrings
```

`DocstringExample` is only required from `docstring_parser.common`; it need not
be re-exported at the package root.

### Enumerations and errors

`DocstringStyle` has members `REST`, `GOOGLE`, `NUMPYDOC`, `EPYDOC`, and
`AUTO`. `RenderingStyle` has members `COMPACT`, `CLEAN`, and `EXPANDED`.
`ParseError` is a `RuntimeError` subclass used for malformed metadata or a
malformed section that the selected parser cannot interpret.

### Parsed structures

All parsed metadata keeps source order in `Docstring.meta`.

```python
class DocstringMeta:
    args: list[str]
    description: str | None

class DocstringParam(DocstringMeta):
    arg_name: str
    type_name: str | None
    is_optional: bool | None
    default: str | None

class DocstringReturns(DocstringMeta):
    type_name: str | None
    is_generator: bool
    return_name: str | None

class DocstringRaises(DocstringMeta):
    type_name: str | None

class DocstringDeprecated(DocstringMeta):
    version: str | None

class DocstringExample(DocstringMeta):
    snippet: str | None

class Docstring:
    short_description: str | None
    long_description: str | None
    blank_after_short_description: bool
    blank_after_long_description: bool
    meta: list[DocstringMeta]
    style: DocstringStyle | None
```

The constructors accept the fields used by the parser:

```python
DocstringMeta(args, description)
DocstringParam(args, description, arg_name, type_name, is_optional, default)
DocstringReturns(args, description, type_name, is_generator, return_name=None)
DocstringRaises(args, description, type_name)
DocstringDeprecated(args, description, version)
DocstringExample(args, snippet, description)
Docstring(style=None)
```

`Docstring.description` joins the short and long descriptions with a newline,
inserting one additional blank line when `blank_after_short_description` is
true. It returns `None` when neither description is present. The properties
`params`, `raises`, `many_returns`, `deprecation`, and `examples` filter `meta`
without changing order. `returns` selects the first return item or `None`.
An absent type, default, return name, version, or snippet is `None`. A dialect
may preserve an explicitly empty description as `""` rather than `None`.

### `parse`

```python
parse(text: str | None, style: DocstringStyle = DocstringStyle.AUTO) -> Docstring
```

Parse one docstring after cleaning leading indentation according to normal
Python docstring conventions. `None`, empty text, and whitespace-only text
produce an empty `Docstring` without metadata.

With an explicit style, parse only that dialect and set `Docstring.style` to
it. With `AUTO`, try the four supported dialects, ignore a `ParseError` when
another dialect succeeds, and return the successful interpretation with the
most structured metadata. Selection is deterministic; equal metadata counts
use the order ReST, Google, Numpydoc, Epydoc. If all dialects reject the text,
raise the parsing error.

### `parse_from_object`

```python
parse_from_object(obj: object, style: DocstringStyle = DocstringStyle.AUTO) -> Docstring
```

Parse `obj.__doc__` using the same rules as `parse`. For a class or module,
also recognize an attribute docstring: a literal string immediately following
an assignment or annotation is associated with that attribute. Its parameter
metadata contains the attribute name, source type text when present, the
literal string as description, and `is_optional=True` with the source default
expression when a default exists.

Only attributes defined directly on a supplied class are included; inherited
class attributes are not traversed. Attribute docstrings inside `__init__` are
not included. If source inspection raises `OSError` or source is unavailable,
return the normal parsed docstring without attribute metadata. For ordinary
functions and other objects, parse only `__doc__`.

### `compose`

```python
compose(
    docstring: Docstring,
    style: DocstringStyle = DocstringStyle.AUTO,
    rendering_style: RenderingStyle = RenderingStyle.COMPACT,
    indent: str = "    ",
) -> str
```

Render a parsed structure as a docstring. `AUTO` uses `docstring.style`; an
explicit style renders in that dialect. Preserve descriptions, metadata order,
optional/default/type information, generator-vs-return information, and blank
description flags. Output is stable and has no trailing blank line.

`COMPACT` keeps metadata descriptions on their header line where supported.
`CLEAN` uses indented continuation lines where supported. `EXPANDED` uses
separate indented description and type lines where supported. `indent` controls
continuation and item indentation.

Dialect formatting uses these conventions:

- ReST uses `:param`, `:type`, `:returns`/`:rtype`, `:yields`, `:raises`, and
  generic `:name args:` fields. Expanded output may put parameter and return
  types in separate fields.
- Google uses headings such as `Args:`, `Attributes:`, `Returns:`, `Yields:`,
  and `Raises:`. Parameters use `name (type): description`; clean optional
  parameters use `, optional`, while compact output may use `?`.
- Numpydoc uses a title followed by a dash underline, then key/value entries
  with indented descriptions. Parameter defaults and optionality are in the
  type line. Example groups retain their `>>>` snippets.
- Epydoc uses `@param`, `@type`, `@return`/`@rtype`, `@yield`/`@ytype`,
  `@raise`, and generic `@name args:` fields. Type fields precede their
  associated parameter or return field.

For each dialect module below, the direct parser and composer signatures are:

```python
parse(text: str | None) -> Docstring
compose(
    docstring: Docstring,
    rendering_style: RenderingStyle = RenderingStyle.COMPACT,
    indent: str = "    ",
) -> str
```

Unlike the top-level `compose`, a dialect-specific `compose` has no `style`
argument.

## ReST parser

The direct module API is `docstring_parser.rest.parse` and
`docstring_parser.rest.compose`.

ReST metadata starts on lines beginning with `:`. The first description line
is `short_description`; remaining description is `long_description`. Record
whether a blank line followed the short description and whether the long
description ended with a blank line.

Recognize parameter keywords `param`, `parameter`, `arg`, `argument`,
`attribute`, `key`, and `keyword`. Accept `:param name: description` and
`:param type name: description`. A type ending in `?` marks the parameter
optional and removes the marker. `:type name: type` supplies a type declared
separately. A description containing `defaults to VALUE` supplies `default`
after removing a final period.

Recognize `return` and `returns` as return metadata, and `yield` and `yields`
as generator-return metadata. A return has zero or one type argument.
Recognize `raises`, `raise`, `except`, and `exception`; a raise has zero or one
exception type argument. Recognize `deprecation` and `deprecated`; when the
description begins with a version followed by text, expose that version.
Recognize `:rtype` including a named form; if a type-only return field has no
corresponding return, create a return item. Unknown fields become
`DocstringMeta` with all field words in `args`. Malformed separators, missing
required names, and too many arguments raise `ParseError`.

## Google parser

The direct module API is `docstring_parser.google.parse`,
`docstring_parser.google.compose`, `GoogleParser`, `Section`, and
`SectionType`.

`SectionType` has `SINGULAR`, `MULTIPLE`, and `SINGULAR_OR_MULTIPLE`.
`Section(title, key, type)` is tuple-like and exposes those three fields.
The stateful parser API is:

```python
GoogleParser(sections=None, title_colon=True)
GoogleParser.parse(text: str | None) -> Docstring
GoogleParser.add_section(section: Section) -> None
```

It recognizes these default headings:

- `Arguments`, `Args`, `Parameters`, `Params` -> parameters;
- `Raises`, `Exceptions`, `Except` -> raises;
- `Attributes` -> attribute parameters;
- `Example`, `Examples` -> singular examples;
- `Returns`, `Yields` -> singular-or-multiple returns.

With `title_colon=True`, a heading requires its colon; with `False`, a
heading is recognized without a colon (a colonized spelling is ordinary
description text). A nonempty caller-provided section collection replaces the
defaults, while `add_section(section)` adds or replaces one section for
subsequent parses. Unknown headings remain description text.

Multiple sections use `name: description`. A parameter may be `name (type):
description`, with a type spanning continuation lines. `, optional` and `?`
mark optional parameters; a description ending in `. Defaults to VALUE.`
provides the default. Return and yield entries expose type, description, and
`is_generator`; raise entries expose exception type and description. In a
return or yield entry, simple PEP 604 unions such as `bytes | memoryview:` and
`Alpha | Beta | Gamma:` are type declarations (with optional whitespace around
`|`), not free-form singular descriptions. Singular return, raise, and example
sections may omit type/name. Invalid entries raise `ParseError`.

## Numpydoc parser

The direct module API is `docstring_parser.numpydoc.parse`,
`docstring_parser.numpydoc.compose`, `NumpydocParser`, `Section`, and
`DEFAULT_SECTIONS`.

`Section(title, key)` declares a section. The stateful parser API is:

```python
NumpydocParser(sections=None)
NumpydocParser.parse(text: str | None) -> Docstring
NumpydocParser.add_section(section: Section) -> None
```

It uses default declarations or a nonempty caller-provided collection;
`add_section` adds or replaces a section. Recognize these default heading
aliases:

- `Parameters`, `Params`, `Arguments`, `Args` -> `param`;
- `Other Parameters`, `Other Params`, `Other Arguments`, `Other Args` ->
  `other_param`;
- `Receives`, `Receive` -> `receives`;
- `Raises`, `Raise` -> `raises`;
- `Warns`, `Warn` -> `warns`;
- `Attributes`, `Attribute` -> `attribute`;
- `Returns`, `Return` -> `returns`;
- `Yields`, `Yield` -> `yields`;
- `Examples`, `Example` -> `examples`;
- `Warnings`, `Warning` -> `warnings`;
- `See Also`, `Related` -> `see_also`;
- `Notes`, `Note` -> `notes`;
- `References`, `Reference` -> `references`;
- Sphinx-style `deprecated` -> `deprecation`.

Headings have a dash underline of matching length. Parameter-like entries are
`name` or `name : type` with an indented, possibly multiline description. A
type ending in `, optional` or `(optional)` sets `is_optional=True`; a default
declaration in the type or a supported default phrase in description sets
`default` and marks optional. Otherwise an explicitly typed parameter has
`is_optional=False`.

Returns/yields accept `name : type` or type-only entries. Raises use the entry
key as `type_name`. Generic sections create `DocstringMeta`. Examples group
consecutive `>>>` lines into `snippet` and following non-command lines into
`description`, producing one `DocstringExample` per group. A deprecated
directive exposes version and optional indented description.

For compatibility, expose compiled patterns named `PARAM_KEY_REGEX`,
`PARAM_OPTIONAL_REGEX`, `PARAM_DEFAULT_REGEX`, and
`PARAM_DEFAULT_REGEX_IN_DESC`. They support the documented parameter forms and
provide named groups `name`, `type`, and `value` used by callers.

## Epydoc parser

The direct module API is `docstring_parser.epydoc.parse` and
`docstring_parser.epydoc.compose`.

Epydoc fields begin with `@`. Recognize `@param name:` and `@keyword name:`
as parameters, `@type name:` as a parameter type, `@ivar name:`, `@cvar
name:`, and `@var name:` as attribute parameters, `@raise:` and `@raise
ExceptionType:` as raises, `@return:`/`@rtype:` and `@yield:`/`@ytype:` as
return or generator-return metadata, and other valid fields as
`DocstringMeta`.

Type and description declarations for the same parameter or return combine
into one item. A type ending in `?` marks optional; `defaults to VALUE` in a
parameter description supplies `default`. Preserve the original field
keyword in `args` where the dialect exposes it. Malformed fields raise
`ParseError`.

## Docstring combination decorator

```python
combine_docstrings(
    *others,
    exclude=(),
    style=DocstringStyle.AUTO,
    rendering_style=RenderingStyle.COMPACT,
)
```

Use this as a decorator on a callable. Parse the decorated callable and each
callable in `others`, combine descriptions and metadata, compose the result,
and assign it to the decorated callable's `__doc__`; return that callable and
preserve its executable behavior.

Only parameters present in the decorated callable's signature appear, in
signature order. For duplicate parameters, the first definition in `others`
order wins; the decorated callable supplies one only when no other source
supplies it. A nonempty decorated short/long description takes precedence;
otherwise use the rightmost nonempty source. Non-parameter metadata is merged
by metadata class, with later sources replacing earlier collections.
`exclude` omits exact metadata classes. Pass `style` and `rendering_style` to
`compose`.

## Example

```python
from docstring_parser import DocstringStyle, parse

doc = parse(
    """
    Brief summary.

    Longer explanation.

    :param int count: number of records
    :returns list[str]: records
    """,
    style=DocstringStyle.REST,
)
assert doc.short_description == "Brief summary."
assert doc.params[0].arg_name == "count"
assert doc.params[0].type_name == "int"
assert doc.returns.type_name == "list[str]"
```

Handle empty input, multiline descriptions, Unicode text, optional/default
parameters, unknown metadata, malformed selected-dialect input, type-only
returns, generator returns, custom Google/Numpydoc sections, and inspectable
class/module attribute docstrings.
