# Build `mistune`

Create a complete, installable Python project named `mistune` from an empty
workspace. The project is a pure-Python Markdown parser compatible with
CommonMark 0.31.2. It must provide HTML, Markdown, reStructuredText, and
abstract-syntax-tree output; configurable block and inline parsers; built-in
plugins and directives; table-of-contents hooks; and a command-line entry
point. Do not depend on a preinstalled copy of Mistune or on runtime network
access.

## Project Description

Mistune turns Markdown text into a token stream and optionally renders those
tokens. The normal high-level paths are:

```python
import mistune

mistune.html("# Title")
markdown = mistune.create_markdown()
markdown("# Title")
ast_parser = mistune.create_markdown(renderer="ast")
ast_parser("# Title")
```

The distribution and import package are both named `mistune`. The package
version is `3.4.0`. It is typed and ships a `py.typed` marker. The library must
remain usable without the test suite, documentation tools, or any third-party
Markdown implementation.

Mistune is a parser and renderer, not an HTML sanitizer. In particular,
`mistune.html` deliberately preserves raw HTML. The escaping and harmful-URL
rules below are part of the public contract and must not be blurred into a
single “safe mode.”

## Supports

- Support Python 3.10 and newer Python 3 versions.
- Provide an installable `src/mistune/` package and a standards-compliant
  `pyproject.toml` using a setuptools build backend.
- Declare the only runtime dependency as
  `typing-extensions; python_version < "3.11"`. On Python 3.11 and newer, the
  installed runtime has no third-party dependency.
- Install both a `mistune` console script and the `python -m mistune` module
  entry point.
- Include the root package, `_inline`, `plugins`, `directives`, and `renderers`
  subpackages, plus `py.typed`.
- Do not require Pygments or a documentation package at runtime. Applications
  may use such packages in custom renderers, but they are not Mistune runtime
  dependencies.
- Keep ordinary in-memory parsing deterministic for fixed text, parser,
  renderer, plugin order, and hook state. File reads are limited to explicit
  `Markdown.read` and include-directive operations.
- Preserve Unicode text, normalize CRLF and lone CR line endings before block
  parsing, and append a final parsing newline internally when one is absent.

## Root Package API

`mistune.__all__` contains these names:

```text
Markdown, HTMLRenderer, BlockParser, BlockState, BaseRenderer,
InlineParser, InlineState, escape, escape_url, safe_entity, unikey,
html, create_markdown, markdown
```

Also expose:

```text
__version__ = "3.4.0"
__homepage__ = "https://mistune.lepture.com/"
```

### `html`

`mistune.html` is a reusable callable `Markdown` instance, not merely an alias
of `markdown()`. It is equivalent to an HTML parser created with raw-HTML
escaping disabled and these plugins enabled in order:

```text
strikethrough, footnotes, table
```

Calling `mistune.html(text)` returns HTML. Raw inline and block HTML is emitted
rather than escaped. Passing `None` produces the empty string.

```python
mistune.html("**hello** <span>world</span>")
# '<p><strong>hello</strong> <span>world</span></p>\n'
```

### `create_markdown`

```python
create_markdown(
    escape: bool | None = None,
    hard_wrap: bool = False,
    renderer: "html" | "ast" | BaseRenderer | None = "html",
    plugins: Iterable[str | Plugin] | None = None,
) -> Markdown
```

Behavior:

- `renderer="html"` creates an `HTMLRenderer`.
- `renderer="ast"` and `renderer=None` select token-list output.
- With a newly created HTML renderer, `escape=None` and `escape=True` both
  escape raw HTML; `escape=False` preserves raw HTML.
- When the caller supplies an `HTMLRenderer` instance, an explicit `escape`
  boolean updates that renderer’s escape behavior. With `escape=None`, retain
  the renderer’s existing setting.
- `hard_wrap=True` changes ordinary soft line breaks into `<br />\n` when
  using the HTML renderer.
- Plugin references may be built-in names, dotted `module.function` strings,
  or callable plugin objects. Apply plugins in input order.
- The historical `speedup` plugin name is accepted but ignored because its
  fast paths are part of the core parser.

A newly created parser has no plugins unless they are supplied.

### `markdown`

```python
markdown(
    text: str,
    escape: bool = True,
    renderer: "html" | "ast" | BaseRenderer | None = "html",
    plugins: Iterable[object] | None = None,
) -> str | list[dict]
```

This convenience function creates or reuses a parser for the requested
configuration, then parses `text`. Its default HTML path escapes raw HTML and
enables no plugins. `renderer="ast"` or `None` returns tokens. Repeated calls
with the same cacheable configuration may reuse parser state configured at
creation time; document and preserve this caching behavior rather than
rebuilding needlessly.

### Utility functions

```python
escape(s: str, quote: bool = True) -> str
escape_url(link: str) -> str
safe_entity(s: str) -> str
unikey(s: str) -> str
```

- `escape` replaces `&`, `<`, and `>` and, when `quote=True`, double quotes.
- `escape_url` resolves valid CommonMark-style character references, then
  percent-encodes characters that are unsafe in a URL while retaining the
  normal RFC 3986 delimiters used by links.
- `safe_entity` resolves accepted character references once and emits escaped
  text, avoiding both raw markup and double-encoding.
- `unikey` collapses whitespace, strips the ends, and returns a
  case-insensitive uppercase key for references and footnotes.

## Markdown Parsing Contract

Implement CommonMark 0.31.2 behavior for the core grammar, including:

- ATX and setext headings;
- paragraphs and blank lines;
- thematic breaks;
- indented and fenced code blocks, including info strings;
- block quotes;
- ordered and unordered tight or loose lists, nesting, continuation lines,
  tabs, and ordered-list start values;
- raw block and inline HTML;
- backslash escapes and character references;
- emphasis and strong emphasis;
- code spans;
- hard and soft line breaks;
- inline links, images, autolinks, and reference links; and
- Unicode content and whitespace without treating all Unicode spaces as ASCII
  indentation.

The parser must retain source order. Nested lists, block quotes, links, images,
and emphasis must terminate at bounded depth rather than recursing without
limit. The default limits are:

```text
BlockParser.max_nested_level = 20
InlineParser.max_emphasis_depth = 20
InlineParser.max_image_depth = 20
```

Callers can provide parser instances with different limits.

## `Markdown`, Parser State, and Hooks

The core constructors are:

```python
BlockParser(
    block_quote_rules: list[str] | None = None,
    list_rules: list[str] | None = None,
    max_nested_level: int = 20,
)
InlineParser(
    hard_wrap: bool = False,
    max_emphasis_depth: int = 20,
    max_image_depth: int = 20,
)
BlockState(parent: object | None = None)
InlineState(env: MutableMapping[str, object])

Markdown(
    renderer: BaseRenderer | None = None,
    block: BlockParser | None = None,
    inline: InlineParser | None = None,
    plugins: Iterable[Plugin] | None = None,
)

Markdown.__call__(s: str) -> str | list[dict]
Markdown.parse(s: str, state: BlockState | None = None)
    -> tuple[str | list[dict], BlockState]
Markdown.read(filepath: str, encoding: str = "utf-8",
              state: BlockState | None = None)
    -> tuple[str | list[dict], BlockState]
Markdown.use(plugin: Plugin) -> None
```

`Markdown.parse` processes one document, returns both the rendered result and
the mutable block state, and invokes hooks in this order:

1. every `before_parse_hooks` callback after input normalization and state
   initialization but before block parsing;
2. every `before_render_hooks` callback after block parsing;
3. rendering or AST materialization;
4. every `after_render_hooks` callback, with each callback receiving and
   returning the current result.

`Markdown.__call__` returns only the result. `Markdown.read` reads bytes,
decodes with the requested encoding, sets `state.env["__file__"]` to the
filepath, and then parses. Normal file and decoding exceptions propagate.

`BlockState` stores the source, tokens, cursor bounds, list tightness, parent,
lazy-line positions, and a shared `env` mapping. A root state starts with a
`ref_links` dictionary. Child states share the parent environment. `InlineState`
stores inline tokens and the same environment along with link/image and
formatting parser state.

`BlockParser.register`, `InlineParser.register`, and `BaseRenderer.register`
add named parser or renderer callbacks and refresh any compiled rule cache.
`Markdown.use` applies a plugin to the live instance, so parser and renderer
configuration persists across later calls.

## AST Output

When no renderer is used, return a JSON-like `list[dict]` token tree. Every
token has a string `type`. Depending on the token, it may also contain:

```text
raw: unparsed string content
children: nested token list
attrs: renderer attributes such as level, url, title, ordered, start, or info
style: source style such as atx, setext, indent, or fenced
marker / bullet / tight: source and list metadata
ref / label: reference-link metadata
```

Core token types include:

```text
blank_line, thematic_break, paragraph, block_text, heading, block_quote,
block_html, block_code, list, list_item, text, emphasis, strong, codespan,
linebreak, softbreak, inline_html, link, image
```

Inline text under a block token is parsed into `children` before the result is
returned. AST output retains semantic source metadata and does not HTML-escape
raw text merely because the HTML renderer would do so.

## Renderers

### `BaseRenderer`

```python
BaseRenderer()
BaseRenderer.register(name: str, method: Callable[..., str]) -> None
BaseRenderer.render_token(token: dict, state: BlockState) -> str
BaseRenderer.render_tokens(tokens: Iterable[dict], state: BlockState) -> str
BaseRenderer.__call__(tokens: Iterable[dict], state: BlockState) -> str
```

Dispatch by token `type`. A registered method receives the renderer as its
first argument. Raise `AttributeError` when no built-in or registered method
exists for a token type.

### `HTMLRenderer`

```python
HTMLRenderer(
    escape: bool = True,
    allow_harmful_protocols: bool | Iterable[str] | None = None,
)
```

Implement render methods for core inline and block tokens. Observable output
uses lowercase HTML tags, double-quoted attributes, `<br />`, `<hr />`, and
`<img ... />`; block renderers normally end in a newline. Code-span and code-
block content is always escaped. Image alt text removes nested markup while
preserving escaped visible text.

`HTMLRenderer.safe_url(url)` applies the URL policy in the Security section.
Plugin installation may register additional HTML methods on the renderer.

### `MarkdownRenderer` and `RSTRenderer`

Expose:

```python
from mistune.renderers.markdown import MarkdownRenderer
from mistune.renderers.rst import RSTRenderer
```

`MarkdownRenderer` reformats a token tree as Markdown and preserves reference
links. It must escape literal block markers, emphasis markers, and backticks
when failing to do so would change meaning on a second parse. It includes
default rendering for task-list and table tokens.

`RSTRenderer` converts supported Markdown tokens to reStructuredText, including
headings, links, images, code, block quotes, and lists. Both renderers are
extensible through `BaseRenderer.register` and subclass overrides.

## Built-in Plugins

The following built-in string names are accepted by `create_markdown` and
`import_plugin`:

```text
speedup, strikethrough, mark, insert, superscript, subscript, footnotes,
table, url, abbr, def_list, math, ruby, task_lists, spoiler
```

Expose their callable forms from their documented submodules. Important syntax
and token behavior:

- `strikethrough`: `~~text~~` -> `strikethrough` / `<del>`.
- `mark`: `==text==` -> `mark` / `<mark>`.
- `insert`: `^^text^^` -> `insert` / `<ins>`.
- `superscript`: `^text^` -> `superscript` / `<sup>`.
- `subscript`: `~text~` -> `subscript` / `<sub>`.
- `footnotes`: inline `[^key]` references plus block definitions, with a
  rendered footnote list and stable indexes.
- `table`: pipe tables with optional leading/trailing pipes and left, center,
  right, or unset alignment. Also expose `table_in_quote` and `table_in_list`
  to enable tables in those nested contexts.
- `url`: turn bare HTTP(S) URLs into normal link tokens.
- `abbr`: replace declared abbreviations while preserving escaped text.
- `def_list`: definition-list blocks with term and item tokens.
- `math`: `$inline$` and `$$` block math. Escape math content when rendered to
  HTML. Also expose `math_in_quote` and `math_in_list`.
- `ruby`: ruby annotation tokens and links around ruby text.
- `task_lists`: transform `[x]` and `[ ]` list items into disabled checkbox
  items with checked state.
- `spoiler`: block spoiler lines and inline `>! ... !<` spans.
- `speedup`: accepted compatibility no-op; output is identical to the core
  parser without the plugin.

A caller may pass a plugin callable directly. A non-built-in string containing
a dotted module path is imported and resolved to a callable. Import and
attribute errors are not silently hidden.

## Directives and Table of Contents

Expose from `mistune.directives`:

```text
DirectiveParser, BaseDirective, DirectivePlugin, RSTDirective,
FencedDirective, Admonition, TableOfContents, Include, Image, Figure
```

`RSTDirective(plugins)` handles `.. name:: title` blocks. `FencedDirective`
handles fenced `{name}` blocks and accepts configurable fence marker
characters. Directive plugins register by name and may return one token or a
list of tokens.

- `Admonition` supports attention, caution, danger, error, hint, important,
  note, tip, and warning sections.
- `TableOfContents(min_level=1, max_level=3)` renders a TOC at the directive
  location and adds IDs to selected headings.
- `Image` and `Figure` render filtered image URLs and escaped attributes.
  Width, height, alignment, class, and figure-width values must not permit CSS
  or attribute injection.
- `Include` is file-backed and is described in the Security section.

Retain the deprecated `RstDirective` compatibility class, which emits a
`DeprecationWarning` and delegates to `RSTDirective`.

Expose:

```python
add_toc_hook(
    md: Markdown,
    min_level: int = 1,
    max_level: int = 3,
    heading_id: Callable[[dict, int], str] | None = None,
) -> None

render_toc_ul(toc: Iterable[tuple[int, str, str]]) -> str
```

The hook stores `(level, id, visible_text)` tuples in
`state.env["toc_items"]`. Default IDs are `toc_1`, `toc_2`, and so on, and
must avoid collisions with IDs already present in raw HTML. Custom IDs and TOC
links are HTML-escaped. `render_toc_ul([])` returns an empty string.

## Security Contract

### Raw HTML escaping

The three high-level defaults intentionally differ:

| API | Raw HTML default |
| --- | --- |
| `mistune.html` | preserved (`escape=False`) |
| `mistune.create_markdown()` | escaped |
| `mistune.markdown()` | escaped |
| command-line tool | preserved unless `--escape` is passed |

With escaping enabled, raw inline HTML becomes escaped text and raw block HTML
is wrapped as escaped paragraph content. With escaping disabled, raw HTML is
passed through. This setting does not disable URL filtering or code escaping.

### URL filtering

By default, `HTMLRenderer.safe_url` permits:

```text
http:, https:, mailto:, tel:, ftp:, ftps:, irc:, ircs:
```

It also permits relative, root-relative, fragment, and query URLs and these
image data prefixes:

```text
data:image/gif;  data:image/png;  data:image/jpeg;  data:image/webp;
```

Before classifying a URL, percent-decode it up to three times, lowercase it,
and discard leading whitespace for the comparison. Known or unknown harmful
schemes—including JavaScript-like, file, executable data, view-source, and
encoded variants—render as `#harmful-link`. SVG data images are not in the
safe data allowlist.

`allow_harmful_protocols=True` disables protocol blocking. An iterable allows
only the supplied normalized prefixes in addition to the normal safe set.
Even when a protocol is allowed, emit the URL with HTML escaping.

### Included files and generated attributes

`Include` requires parsing through `Markdown.read` or an equivalent state with
`env["__file__"]`. Resolve include paths relative to that source file and:

- reject absolute paths and paths whose real location escapes the source
  directory;
- reject self-includes and circular include chains;
- return rendered error blocks for missing source context or missing files;
- recursively parse Markdown extensions after normalizing line endings;
- treat HTML extensions as block HTML subject to the renderer’s escape mode;
- render other text in an include block and escape it when HTML escaping is on.

Image and figure directive attributes, heading IDs, TOC hrefs, math content,
code content, and image alt/title text must be escaped in their HTML attribute
or text context. Dimension options accept numeric values with supported units,
not arbitrary CSS declarations.

### Resource behavior

Malformed or deeply nested brackets, links, images, emphasis, formatting,
ruby, spoilers, math, tables, definition lists, blank list continuations, and
reference-link sets must terminate without unbounded recursion or obvious
quadratic backtracking. Preserve the configurable depth limits. Do not add
wall-clock sleeps or network lookups to parsing.

## Command-Line Interface

Install both of these equivalent entry points:

```text
mistune
python -m mistune
```

Supported options:

```text
-m, --message MESSAGE
-f, --file FILE
-p, --plugin NAME [NAME ...]
--escape
--hardwrap
-o, --output OUTPUT
-r, --renderer RENDERER
--version
```

Behavior:

- Read `--message` when supplied, otherwise `--file`, otherwise piped stdin.
- If no usable message, file, or piped input exists, print an explanatory
  message and exit with status 1.
- Default CLI plugins are `strikethrough`, `footnotes`, and `table`. Supplying
  `--plugin` replaces that default list.
- The default renderer is HTML. Accept `rst` and `markdown` for the bundled
  alternate renderers.
- The CLI preserves raw HTML by default; `--escape` enables escaping.
- `--hardwrap` converts soft line breaks according to the inline parser option.
- Write output files as UTF-8. Configure stdout for UTF-8 when supported.
- `--version` prints `mistune 3.4.0`.

## Implementation Notes

- Keep parser, state, renderer, plugin, and directive objects reusable. Their
  registered rules and hooks are live mutable configuration.
- Keep token order, list order, plugin order, and hook order stable.
- Do not make trusted behavior depend on hash iteration, random values, the
  current time, or network services.
- Performance guards are semantic safety requirements, but exact elapsed time
  varies by interpreter and machine. Implement bounded parsing behavior rather
  than special-casing benchmark-sized strings.
- Do not copy a public Mistune wheel or source tree into the generated project.
  Recreate the package from this behavior contract and include normal project
  metadata, licensing, typing marker, and console entry point.
