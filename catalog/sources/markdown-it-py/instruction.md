# Build `markdown-it-py`

## Project Description

Create the `markdown_it` project from an empty workspace. This is a repository-generation task for the frozen `python` package contract, task specification version `0.1.0`, at source revision `bff75edcd7e6ce68f417803361d6e9f1223ad373`. Implement the public behavior described by the local inventories and the task-specific detail below; do not copy upstream source or tests. The supported scope is python, markdown, parser, renderer, tokens, html, separate-verifier.

## Natural Language Instruction

Starting with an empty `workspace/`, create an installable `markdown_it` project. Implement every public/core API named in the API Usage Guide, its package exports, and its documented integration points. Preserve observable input types, return shapes, ordering, determinism, state changes, and documented exception behavior. The project must be usable through its declared `markdown_it` import path (or the package root for this Node task), and all required modules must be present in the directory structure below.

The task-specific specification retained below supplies the detailed behavior for each API family. Treat it as the contract: do not add unrelated APIs, replace deterministic behavior with randomized or time-dependent behavior, or weaken error handling.

## Supports

- Language/runtime: `python` on `3.12.11`; target environment metadata declares `debian-12-amd64`.
- Distribution/package: `markdown_it`; import/root name: `markdown_it`. Package manager: `pip`.
- Install from the repository root with `python -m pip install . --no-deps`. Build metadata must be complete and agree with the package entry point.
- Dependency status in the frozen source metadata is `known`. Use only dependencies declared by the task and available in the preinstalled build image; standard-library modules are not third-party runtime dependencies.
- NoNetwork boundary: agent, candidate, verifier, Oracle, and controls run with `network_mode=no-network`. Do not access GitHub, PyPI, npm registries, Go proxy, DNS, or external services at runtime. Do not fetch source or dependencies during implementation or package use.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── markdown_it/
│   └── __init__.py
└── README.md
```

The tree is the minimum public project layout. Add a module only when it corresponds to a documented import path or package resource. Do not place publicly unavailable evaluator code, non-public evaluation material, Oracle payloads, dependency caches, or trusted reports in this workspace.

## API Usage Guide

The public/core API families recorded in the local inventory are: Explicit boundaries, Root package and metadata, `MarkdownIt`, `Token`, `SyntaxTreeNode`, Renderer and rule components, CLI and helpers.

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
import_or_require = "markdown_it"
```

The retained task-specific examples below provide ordinary API calls and combinations grounded in the frozen inventory. Keep their result shapes and ordering exact.

## Error Handling and Boundary Conditions

- Empty inputs, malformed values, missing resources, duplicate values, and unsupported options must follow the task-specific error contracts below; do not silently coerce or discard information unless explicitly specified.
- Repeated calls must remain deterministic. Filesystem, process, clock, random, native, callback, and serialization boundaries are supported only where the local specification documents them.
- Network attempts are prohibited and must not be used as a fallback. Installation failures, missing offline dependencies, or unsupported external capabilities are environment/source concerns, not reasons to invent behavior.


## Source-derived task detail

# Build `markdown-it-py`

Create an installable Python distribution named `markdown-it-py` from an empty
workspace. The import package is `markdown_it`. Implement the deterministic,
local Markdown parser and token model described below. The package must not
depend on a preinstalled copy of `markdown-it-py`, on network access during
the agent run, or on source files outside the project being built.

## Project Description

`markdown-it-py` is a Python port of the markdown-it parser. It converts
Markdown source into a token stream and HTML, with configurable block and
inline rules, presets, renderer hooks, and a small token tree representation.
The scored contract is the core parser, renderer, token, tree, ruler, preset,
URL-normalization, and command-line argument surface. It is deliberately
bounded to deterministic local behavior.

The frozen reference distribution is version `4.2.0`. The source package is
pure Python apart from its one required runtime dependency, `mdurl`.

## Supports

- Support CPython 3.10 or newer, including Python 3.12.
- Install from the project root with `python -m pip install .` when the
  build-stage hash-locked dependencies are available.
- Provide a package directory named `markdown_it` and a PEP 561 `py.typed`
  marker.
- Expose the distribution version `4.2.0` as `markdown_it.__version__`.
- Require exactly the runtime dependency `mdurl~=0.1`; do not require
  `mdit-py-plugins`, `linkify-it-py`, Graphviz, or other optional packages for
  the core contract.
- Keep parsing, rendering, token conversion, and tree inspection deterministic
  and local. Do not call a network, service, shell command, or subprocess for
  normal API use.
- Use only the standard library when an optional feature is unavailable.
  `linkify-it-py` is optional and may be absent; `MarkdownIt(...).linkify` may
  therefore be `None` unless the optional package is installed.

### Explicit boundaries

The following are outside the scored contract and must not be required:

- third-party plugin packages such as `mdit-py-plugins`;
- live URL fetching, DNS, or other external services;
- benchmark, fuzzing, documentation, and test fixture data from the upstream
  repository; and
- interactive CLI input processing after argument parsing.

The `markdown-it` command entry point must still be declared and its argument
parser must support the local `--stdin` flag and positional filenames.

## API Usage Guide

### Root package and metadata

The root package exports `MarkdownIt` and `__version__`. The following imports
must work:

```python
from markdown_it import MarkdownIt
from markdown_it.token import Token
from markdown_it.tree import SyntaxTreeNode
from markdown_it.renderer import RendererHTML, RendererProtocol
```

`repr(MarkdownIt("commonmark"))` is
`"markdown_it.main.MarkdownIt()"`. The package must expose a `py.typed` file.

### `MarkdownIt`

```python
MarkdownIt(
    config: str | Mapping[str, object] = "commonmark",
    options_update: Mapping[str, object] | None = None,
    *,
    renderer_cls: Callable[[MarkdownIt], RendererProtocol] = RendererHTML,
)
```

The named presets `"default"`, `"js-default"`, `"zero"`, `"commonmark"`,
`"gfm-like"`, and `"gfm-like2"` are accepted. A mapping configuration has an
`options` mapping and may have `components` rule selections. Unknown preset
names raise `KeyError`; an empty configuration raises `ValueError`.

The default `commonmark` options are accessible through the mapping-like
`md.options` object. They include `html`, `linkify`, `typographer`, `quotes`,
`breaks`, `langPrefix`, `xhtmlOut`, `highlight`, and `maxNesting`. Attribute
style access and item style access are both supported for these option names.
`md["inline"]`, `md["block"]`, `md["core"]`, and `md["renderer"]` return the
corresponding parser or renderer component.

```python
md = MarkdownIt("commonmark", {"breaks": True})
tokens = md.parse("# title\n\nbody")
html = md.render("# title\n\nbody")
inline_tokens = md.parseInline("a *word*")
inline_html = md.renderInline("a *word*")
```

`parse(src, env=None)` returns a list of `Token` objects. `src` must be a
string and `env` must be a mutable mapping when supplied; invalid inputs raise
`TypeError`. The parser preserves block order and stores inline token children
on the `inline` token. A supplied `env` mapping is updated by reference
definition processing and is passed through rendering.

`render(src, env=None)` parses and renders the source with `RendererHTML`.
For the commonmark preset, for example:

```python
MarkdownIt("commonmark").render("# Hello\n\nThis is **bold**.")
# '<h1>Hello</h1>\n<p>This is <strong>bold</strong>.</p>\n'
```

The core contract includes headings, paragraphs, emphasis, strong emphasis,
links and reference links, inline code, escaped characters, entities,
blockquotes, unordered and ordered lists, thematic breaks, fenced code blocks,
backslash line breaks, and safe HTML escaping when `html=False`. The default
preset additionally supports strikethrough and tables.

`parseInline` and `renderInline` use the inline pipeline without block
wrappers. `renderInline` returns HTML text without a surrounding paragraph.

The chainable methods are:

```python
md.set(options: Mapping[str, object]) -> None
md.configure(config: str | Mapping[str, object], options_update=None) -> MarkdownIt
md.enable(names: str | Iterable[str], ignoreInvalid=False) -> MarkdownIt
md.disable(names: str | Iterable[str], ignoreInvalid=False) -> MarkdownIt
md.reset_rules()  # context manager restoring active rules on exit
md.use(plugin: Callable, *params, **options) -> MarkdownIt
md.add_render_rule(name: str, function: Callable, fmt="html") -> None
md.get_all_rules() -> dict[str, list[str]]
md.get_active_rules() -> dict[str, list[str]]
```

Enabling or disabling an unknown rule raises `ValueError` unless
`ignoreInvalid=True`. A plugin receives the parser and may register a local
core rule. `use` returns the same parser instance.

`validateLink(url: str) -> bool` rejects dangerous URL schemes such as
`javascript:`. `normalizeLink(url: str) -> str` percent-encodes Unicode URL
characters while preserving URL structure. `normalizeLinkText(link: str) ->
str` normalizes link display text without applying URL percent encoding.

### `Token`

```python
Token(
    type: str,
    tag: str,
    nesting: Literal[-1, 0, 1],
    attrs: dict[str, str | int | float] | list[list[object]] | None = None,
    map: list[int] | None = None,
    level: int = 0,
    children: list[Token] | None = None,
    content: str = "",
    markup: str = "",
    info: str = "",
    meta: dict[object, object] | None = None,
    block: bool = False,
    hidden: bool = False,
)
```

`Token` is a slots dataclass. `attrs` is normalized to a dictionary; a falsey
value becomes `{}`, and a list of pairs is converted with `dict`. The token
methods are:

```python
attrIndex(name: str) -> int
attrItems() -> list[tuple[str, object]]
attrPush((name, value)) -> None
attrSet(name, value) -> None
attrGet(name) -> object | None
attrJoin(name, value: str) -> None
copy(**changes) -> Token
as_dict(*, children=True, as_upstream=True, meta_serializer=None,
        filter=None, dict_factory=dict) -> MutableMapping
Token.from_dict(mapping) -> Token
```

`attrJoin` appends with one space and rejects an existing non-string value.
`as_dict(as_upstream=True)` represents empty attrs as `None` and non-empty attrs
as a list of pairs; nested children are recursively converted. `from_dict`
reconstructs nested children.

### `SyntaxTreeNode`

`SyntaxTreeNode(tokens: Sequence[Token])` creates a read-only navigable tree
view over a token sequence. Its public behavior includes `type`, `tag`,
`attrs`, `map`, `level`, `content`, `markup`, `info`, `meta`, `block`,
`hidden`, `children`, `parent`, `siblings`, `next_sibling`,
`previous_sibling`, `is_root`, `is_nested`, `to_tokens()`, `walk()`, and
`pretty()`. Integer and slice indexing address children. Root representation is
`SyntaxTreeNode(root)`. `to_tokens()` recreates the opening/inline/closing
token sequence with nested children.

### Renderer and rule components

`RendererHTML` renders a token list with the configured options. A subclass
may override token-type methods such as
`text(tokens, idx, options, env) -> str` and may be passed as `renderer_cls`.
`RendererProtocol` describes the renderer interface.

`ParserCore`, `ParserBlock`, and `ParserInline` expose a `ruler` object. The
`Ruler` API includes `at`, `before`, `after`, `push`, `enable`, `enableOnly`,
`disable`, `getRules`, `get_all_rules`, and `get_active_rules`. Rule callbacks
receive the parser state (or state and a silent flag for inline rules) and are
called in configured order.

### CLI and helpers

`markdown_it.cli.parse.parse_args(args: Sequence[str] | None) -> Namespace`
accepts `--stdin`, `-v/--version`, and zero or more filenames. The declared
`markdown-it` entry point uses this parser. `markdown_it.common.utils.unescapeAll`
decodes supported Markdown entities and escapes. `markdown_it.utils.OptionsDict`
supports mutable mapping operations plus option properties.

## Implementation Notes

Preserve deterministic child order in tokens and rule lists. Use a separate
candidate-owned implementation; do not copy the frozen repository or upstream
tests into the generated project. Optional packages may be detected, but core
construction and rendering must remain complete without them.

The grader invokes the installed package through a bounded child-side JSON
adapter. Do not write grading, reward, JUnit, or collection files. Do not
assume the verifier tests are present in the candidate workspace. The source
revision is the behavior reference, while the fixed verifier scenarios are
the scored denominator.
