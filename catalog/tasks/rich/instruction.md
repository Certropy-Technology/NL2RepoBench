# Build `rich`

Create a complete, installable Python project named `rich` from an empty
workspace. The project is a terminal rendering library: it turns structured
Python objects and text into deterministic plain-text or ANSI terminal output.
Implement the documented public behavior without copying the upstream source,
tests, or implementation strategy. Do not depend on a preinstalled `rich`, on
network access at runtime, or on the verifier's test files.

## Project Description

Rich provides composable renderables for terminal applications. It supports
styled text, colors, tables, panels, layouts, trees, markdown, syntax
highlighting, pretty representations, progress/live displays, tracebacks, and
JSON rendering. The core library must work with ordinary file-like objects, not
only an interactive TTY. Rendering must honor an explicit console width and
terminal/color policy so that captured output can be compared byte-for-byte.

This is a repository-generation task. Starting from an empty directory, create
an installable package with the upstream import layout (`rich/`), package
metadata, `rich/py.typed`, and the modules needed by the public APIs below.
Do not add a custom command-line protocol: the deterministic subprocess
boundary in `candidate-boundary.json` is an audit contract for a future
separate verifier adapter, not an extra package API.

## Supports

- Support CPython 3.9 and newer versions in the frozen test environment.
- Use a normal installable package and preserve the `rich` import path.
- Core runtime dependencies are Pygments and markdown-it-py (with mdurl as its
  locked transitive dependency). The optional `jupyter` extra is not required
  for the core candidate and must not be imported during ordinary console use.
- Normal rendering is local and offline. Do not fetch files, call services, or
  require a terminal device merely to construct renderables or render to a
  `StringIO`/file.
- Preserve Unicode text, ANSI escape sequences, markup escaping, and Python
  file-like-object semantics.

## API Usage Guide

The names below are the public behavior surface for the candidate. Compatible
aliases and additional documented modules may be implemented, but do not make
undocumented private implementation details part of the contract.

### Root helpers

`rich.get_console() -> Console` returns the process-global console,
`rich.reconfigure(*args, **kwargs) -> None` replaces its configuration,
`rich.print(*objects, sep=" ", end="\n", file=None, flush=False) -> None`
renders through a console, and `rich.print_json(json=None, *, data=None,
indent=2, highlight=True, skip_keys=False, ensure_ascii=False,
check_circular=True, allow_nan=True, default=None, sort_keys=False) -> None`
renders valid JSON data. `rich.inspect()` renders a stable inspection view of
an object when a caller explicitly requests it.

### Console and capture

`rich.console.Console` accepts a file-like `file`, explicit `width`,
`color_system` (including `None`), `force_terminal`, `record`, `markup`,
`emoji`, `soft_wrap`, and related documented options. Its `print()` method
accepts strings and renderables, applies `sep` and `end`, and writes only to
that console's file. `print_json()` accepts a JSON string or JSON-compatible
`data`; invalid JSON raises the normal decoder error. `rule()`, `log()`,
`clear()`, `status()`, and `screen()` provide their documented terminal
helpers without changing captured output behind the caller's back.

`Console.capture()` is a context manager. Within the context, printed output
is captured; `CaptureResult.get()` returns the captured text. The explicit
`begin_capture()` / `end_capture()` pair has equivalent capture semantics.
When `record=True`, `export_text(clear=False, styles=False)`,
`export_html(clear=False, inline_styles=False, code_format=None)`, and
`export_svg(title="Rich")` export the recorded render. A fresh console must
not contain output recorded by another console.

For deterministic tests, callers will provide `file=io.StringIO()`, a fixed
`width`, `color_system=None` for plain text, and `force_terminal=False` unless
ANSI behavior is the subject of the check. Do not infer width or color from the
host terminal when these options are explicit.

### Text, style, color, and segments

`rich.text.Text` represents styled text. Support construction from a string,
`Text.from_markup(text, *, style=None, emoji=True, justify=None, overflow=None,
end="\n")`, and `Text.from_ansi(text)`. `append()`, `append_text()`,
`stylize()`, `copy()`, `plain`, `style`, and `cell_len` preserve text content
and span ordering. Literal square brackets can be escaped when markup parsing
is enabled; malformed markup follows the documented markup error behavior.

`rich.style.Style` and `rich.color.Color` parse named colors, attributes, and
hex/rgb specifications. `Style.parse()` and `Color.parse()` are deterministic;
invalid specifications raise the documented `StyleSyntaxError` or
`ColorParseError`. `rich.segment.Segment` stores text plus optional style and
control information and supports splitting/line processing as documented.

### Composable renderables

Implement the ordinary construction and rendering behavior of:

- `Table` (columns, rows, headers, borders, box, widths, justification, and
  stable row order), `Panel`, `Rule`, `Tree`, `Columns`, `Align`, `Padding`,
  `Group`, and `Layout`;
- `Markdown`, including headings, emphasis, code spans/fences, links, lists,
  block quotes, and escaped markup;
- `Syntax` with a source string, lexer/language choice, theme, line numbers,
  and fixed-width rendering;
- `Pretty` and `JSON` for deterministic structured values;
- `Theme` for named style lookup and explicit fallback behavior.

Renderables may implement the console render protocol, but rendering the same
value with the same console options must not depend on object addresses,
iteration over unordered data, wall-clock time, or terminal dimensions that
were not explicitly requested.

### Live and progress components

`Live`, `Progress`, `Spinner`, and `Status` provide refreshable terminal views.
Support their non-interactive/file-backed lifecycle sufficiently for callers to
start, update, refresh, and stop them, and ensure context managers clean up on
exceptions. Tests that require a real TTY, cursor movement, wall-clock timing,
or background refresh must not be emulated by sleeping forever or by requiring
network access. A verifier may isolate or exclude platform-specific and
 timing-sensitive cases under the frozen policy; ordinary static rendering must
remain deterministic.

### Tracebacks, logging, and protocol behavior

`rich.traceback.Traceback` and `install()` render exceptions with the documented
options, including chained exceptions and optional local-variable display.
`RichHandler` integrates with the standard logging package without corrupting
unrelated handlers. `rich.protocol.is_renderable()` and the console render
protocol distinguish supported renderables from unsupported values using the
normal type/error contract.

## Implementation Notes

- Preserve public import paths and re-exports for the modules exercised by the
  official tests. Keep exception types and sentinel identity stable.
- Plain-text capture must use `\n` line endings. ANSI output is only expected
  when the caller explicitly enables a color system or forced terminal.
- Width, encoding, locale, `TERM`, `COLUMNS`, `LINES`, and clock behavior must
  be fixed by the caller in deterministic tests; never bake the host values
  into the library.
- Do not include `tests/`, test fixtures, a reference implementation, or a
  reward/result writer in the generated repository.
