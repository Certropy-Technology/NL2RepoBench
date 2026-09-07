# Build `Pygments`

## Project Description

Create a complete, installable Python distribution named `Pygments` from an
empty workspace. It is a pure-Python syntax-highlighting library that turns
source text into `(token_type, text)` streams and formats those streams as
HTML, terminal ANSI, LaTeX, RTF, SVG, and related outputs. The implementation
must be usable as both the `pygments` import package and the `pygmentize`
command-line program.

## Supports

- Support CPython 3.9 and newer Python 3.x versions; evaluation uses CPython
  3.12 on Linux.
- Install from the repository root with `python -m pip install .`.
- Use a standard `pyproject.toml` build configuration and expose version
  `2.21.0`.
- Declare no third-party runtime dependency. Optional terminal color support
  may be omitted; ordinary library and CLI behavior must work without it.
- Keep normal operation local and deterministic. The agent and verifier run
  without network access. Do not retrieve the reference repository or install
  packages at runtime.

## Natural Language Instruction

Create the `Pygments` Python project from an empty `workspace/`. Implement a
usable pure-Python lexer and formatter library, not a table of answers for a
few snippets. At minimum, provide the token model, lexer lookup registry,
representative language lexers, formatter lookup, style lookup, utility
helpers, and the `pygmentize` command described in this document. Preserve
source text order, deterministic output, documented exceptions, and both root
and submodule import paths.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── LICENSE
├── pygments/
│   ├── __init__.py
│   ├── __main__.py
│   ├── token.py
│   ├── lexer.py
│   ├── lexers/__init__.py
│   ├── lexers/python.py
│   ├── formatters/__init__.py
│   ├── formatters/html.py
│   ├── styles/__init__.py
│   ├── filters/__init__.py
│   └── util.py
└── README.md
```

The package root must expose `lex`, `format`, `highlight`, and `Token`. The
`pygmentize` console entry point may call `pygments.cmdline:main` or an
equivalent module, but it must read stdin/files locally and write only the
requested output stream.

## API Usage Guide

### Root functions

`pygments.lex(code, lexer)` accepts text or bytes and a lexer instance and
returns an iterable of `(TokenType, text)` pairs. `pygments.format(tokens,
formatter, outfile=None)` writes to a file-like object when supplied, or
returns a string/bytes result. `pygments.highlight(code, lexer, formatter,
outfile=None)` composes the two operations.

### Tokens and lexers

`pygments.token.Token` is a lazily nested singleton token tree. Attribute access
such as `Token.Name.Function` creates/retrieves a token type; token types are
tuples, have stable `repr` values such as `Token.Name.Function`, support
membership tests, and expose `split()`. Provide standard aliases including
`Text`, `Keyword`, `Name`, `String`, `Number`, `Operator`, `Punctuation`,
`Comment`, `Generic`, and `Error`.

The public `pygments.lexer` module provides `Lexer`, `RegexLexer`,
`ExtendedRegexLexer`, `DelegatingLexer`, `LexerContext`, `include`, `inherit`,
`bygroups`, `using`, `this`, `default`, `words`, and `line_re`. A lexer accepts
options such as `stripnl`, `stripall`, `ensurenl`, `tabsize`, and `encoding`.
`get_tokens(text)` yields tokens and `get_tokens_unprocessed(text)` yields
`(position, token_type, text)` triples. Regex lexers use ordered state rules.

`pygments.lexers` provides `get_all_lexers`, `find_lexer_class`,
`find_lexer_class_by_name`, `get_lexer_by_name`, `get_lexer_for_filename`,
`get_lexer_for_mimetype`, `guess_lexer`, and `guess_lexer_for_filename`.
Lookup returns configured lexer instances and raises `ClassNotFound` when no
match exists. Built-in metadata must include Python, JavaScript, HTML/XML,
JSON, SQL, Bash, Ruby, and C.

### Formatters, styles, utilities, and CLI

`pygments.formatter.Formatter` is the base formatter. The formatters package
provides `HtmlFormatter`, `TerminalFormatter`, `Terminal256Formatter`,
`LatexFormatter`, `RtfFormatter`, and `SvgFormatter`, plus lookup helpers.
`HtmlFormatter` escapes source text, supports `linenos`, `cssclass`, `nowrap`,
and `full`, and exposes deterministic `get_style_defs()` output. Styles are
available through `pygments.styles.get_style_by_name`.

Implement `ClassNotFound`, `OptionError`, `get_bool_opt`, `get_int_opt`,
`get_list_opt`, `get_choice_opt`, `html_escape`, `guess_decode`,
`duplicates_removed`, `shebang_matches`, `Filter`, and `apply_filters`.

Install the `pygmentize` entry point. It must read source from a file or stdin,
select a lexer with `-l` or by filename, select a formatter with `-f`, write
to stdout or `-o FILE`, print help with `-h`, and exit nonzero for invalid
lexer or formatter names.

## Implementation Notes

Use a package layout rooted at `pygments/` and keep public re-exports stable.
Preserve token order and exact source text. Lookup tables may be lazy-loaded,
but selected lexers and formatters must be fully functional. Implement
reusable token, regex-state, lookup, formatter, style, filter, and CLI
abstractions rather than hard-coding only the examples above.

## Examples

```python
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

html = highlight('answer = 42\n', PythonLexer(), HtmlFormatter())
```

```python
from pygments.token import Token

token = Token.Name.Function
assert repr(token) == 'Token.Name.Function'
assert Token.Name in token
```

```console
$ printf 'x = 1\n' | pygmentize -l python -f terminal
```

## Error Handling and Boundary Conditions

Unknown lexer, formatter, style, filename, or MIME lookups raise
`ClassNotFound` or the documented lookup exception rather than returning a
random fallback. Bytes input follows the declared encoding behavior. An
outfile receives the rendered value and the high-level function returns the
documented result. CLI invalid options exit nonzero and help exits
successfully.
