# Build `prompt_toolkit`

## Project Description

Create a complete, installable Python package named `prompt_toolkit` from an
empty workspace. It is a pure-Python toolkit for building interactive command
line applications: it parses terminal key sequences, maintains editable text
buffers, renders formatted content, offers completion/history/validation, and
provides reusable layouts, widgets, styles, and dialogs.

The package must work as a library. Do not build a separate application or
network service. The public API is spread across `prompt_toolkit` and its
documented subpackages; preserve the import paths and public re-exports listed
below. Objects supplied by callers, including callbacks, completers, input
streams, output streams, validators, and style objects, must remain usable
without requiring global singleton state.

## Supports

- Support CPython 3.10 and newer on POSIX systems. Keep the source portable to
  Windows, where the package selects Win32 input/output implementations.
- Use a `src/prompt_toolkit/` package layout and provide `pyproject.toml` so
  `python -m pip install -e .` works from the project root.
- Set the distribution name to `prompt_toolkit` and the package version to
  `3.0.53`. `prompt_toolkit.__version__` and `prompt_toolkit.VERSION` must be
  available lazily from installed package metadata.
- Declare `wcwidth>=0.1.4` as the only required runtime dependency. Build
  tooling and pytest are development dependencies. Pygments, `pyperclip`, and
  `asyncssh` are optional integrations and must not be imported eagerly by the
  core package.
- Include `prompt_toolkit/py.typed`. A README and BSD-3-Clause license notice
  are required package metadata, but no test files supplied by an evaluator
  may be required for importing or installing the package.
- Core behavior must be deterministic for a fixed input stream, output size,
  environment, and callback result. Do not compare terminal escape output
  without fixing the selected `ColorDepth` and terminal dimensions.
- A real terminal is not available to ordinary non-interactive processes.
  Code using the default input/output factories must handle a pipe or missing
  TTY as documented below; tests and examples should inject `PipeInput`,
  `DummyInput`, `DummyOutput`, or a controlled text stream when a real terminal
  is not required.

## Public API Usage Guide

### Root module

`import prompt_toolkit` must expose these names through the root module:

```python
Application
prompt
choice
PromptSession
print_formatted_text
HTML
ANSI
__version__
VERSION
```

`prompt(message="", **kwargs) -> str` creates a one-shot prompt session and
returns accepted text. `choice(message, options, **kwargs)` prompts for one
item and returns the selected value. `PromptSession(**kwargs)` is reusable;
`session.prompt(message="", **kwargs) -> str` and
`await session.prompt_async(message="", **kwargs) -> str` accept input,
validate it, update history, and return only after acceptance, EOF, or an
interrupt. `accept_default=True` accepts the supplied default without waiting
for another key. `KeyboardInterrupt` and `EOFError` retain their normal
meaning and must not be converted into an ordinary empty result.

`print_formatted_text(*values, file=None, end="\n", flush=False, style=None,
color_depth=None, **kwargs)` renders formatted text to the selected file. It
uses a plain-text output when the destination is not a TTY and a terminal
output when it is a TTY. Explicit `color_depth` and a supplied file override
environment-based detection.

### Application and sessions

`prompt_toolkit.application.Application` represents one running UI:

```python
Application(
    layout=None,
    style=None,
    input=None,
    output=None,
    full_screen=False,
    mouse_support=False,
    erase_when_done=False,
    editing_mode=EditingMode.EMACS,
    key_bindings=None,
    clipboard=None,
    color_depth=None,
    refresh_interval=None,
    refresh_in_thread=False,
    pre_run=None,
    after_render=None,
    reverse_vi_search_direction=False,
    include_default_pygments_style=True,
    cursor=None,
)
```

The constructor stores the supplied layout, input, output, style, key
bindings, clipboard, and editing mode. `run()` runs synchronously and
`run_async()` runs asynchronously; both enter the input raw mode, process key
events, render invalidated screens, and restore terminal state on exit.
`exit(result=None, exception=None, style="")` requests completion, while
`invalidate()` schedules a redraw. `is_running()` and `is_done()` report the
current state, and `current_buffer` returns the focused `Buffer`.

`create_app_session(input=None, output=None)` is a context manager that makes
an application session current for nested calls. `create_app_session_from_tty`
opens the controlling terminal on POSIX and selects the platform input/output
pair. `get_app()`, `get_app_or_none()`, and `get_app_session()` retrieve the
current objects; `set_app(app)` temporarily overrides the current application.
Nested contexts must restore their previous values.

### Input and output

`prompt_toolkit.input.Input` defines `fileno()`, `read_keys()`,
`typeahead_hash()`, `raw_mode()`, `cooked_mode()`, `attach(callback)`,
`detach()`, `closed`, and `close()`. `PipeInput` adds `send_bytes(data)` and
`send_text(data)` for deterministic tests. `DummyInput` immediately reports
EOF to an application. `create_pipe_input()` returns a context manager whose
pipe can be fed with text before `Application.run()` or `PromptSession.prompt()`.

`create_input(stdin=None, always_prefer_tty=False)` selects `Vt100Input` on
POSIX and `Win32Input` on Windows. When no usable file descriptor exists it
returns `DummyInput`; `always_prefer_tty` may select a TTY from stdout/stderr
when stdin is redirected. POSIX input must decode UTF-8 and parse ordinary
characters, control keys, VT100 escape sequences, bracketed paste, and cursor
position responses. Windows input must use the Win32 console APIs without
being imported on POSIX.

`prompt_toolkit.output.Output` provides methods for writing text and raw
terminal sequences, flushing, querying size, changing title, cursor movement,
screen/alternate-screen management, mouse support, bracketed paste, cursor
shape, and color attributes. `DummyOutput` is a no-op output with a stable
`Size(rows=40, columns=80)`. `create_output(stdout=None,
always_prefer_tty=False)` returns `PlainTextOutput` for redirected POSIX output,
`Vt100_Output` for a POSIX TTY, and the appropriate Win32/Windows 10/ConEmu
implementation on Windows. Respect `TERM`, `NO_COLOR`,
`PROMPT_TOOLKIT_BELL`, and `PROMPT_TOOLKIT_COLOR_DEPTH`.

`ColorDepth` has `DEPTH_1_BIT`, `DEPTH_4_BIT`, `DEPTH_8_BIT`, and
`DEPTH_24_BIT` values plus the aliases `MONOCHROME`, `ANSI_COLORS_ONLY`,
`DEFAULT`, and `TRUE_COLOR`. `ColorDepth.from_env()` returns an explicit
environment choice or `None`.

### Documents and buffers

`Document(text="", cursor_position=None, selection=None)` is an immutable
view of text and cursor state. Its properties include `text`,
`cursor_position`, `selection`, `current_char`, `char_before_cursor`,
`text_before_cursor`, `text_after_cursor`, `current_line`, `lines`,
`line_count`, `cursor_position_row`, `cursor_position_col`, and word/line
queries. Cursor positions are zero-based and may be immediately after the
last character. Equality compares text, cursor position, and selection.

`Buffer(...)` is mutable editor state around a `Document`. It supports
`reset()`, text/cursor/document properties, undo/redo, insertion/deletion,
cursor movement, line joining, history navigation, completion navigation,
search, selection/cut/copy/paste, newline insertion, validation, and
asynchronous completion/validation. `insert_text(text, overwrite=False,
move_cursor=True)` updates text and cursor position; `delete()` and
`delete_before_cursor()` return the removed text. Read-only buffers reject
mutations unless an internal bypass is explicitly requested by the owning
application. Completion and history callbacks may be synchronous or
asynchronous and must not corrupt the buffer when a result arrives late.

### History, clipboard, and validation

`History.load()` is an async generator yielding entries newest first.
`InMemoryHistory`, `FileHistory`, and `ThreadedHistory` implement in-memory,
file-backed, and background-thread loading. `append_string()` stores a new
entry; `get_strings()` returns loaded entries oldest first. File history uses
the supplied path and preserves entries across instances.

`ClipboardData(text="", type=SelectionType.CHARACTERS)` stores plain text and
selection type. `Clipboard` defines `set_data`, `set_text`, `rotate`, and
`get_data`. `DummyClipboard` is a no-op; `InMemoryClipboard` stores a kill
ring; `DynamicClipboard` delegates to a clipboard selected by a callback.
Clipboard operations used by Emacs and Vi bindings must preserve line versus
character selection types.

`ValidationError(cursor_position=0, message="")` is an exception carrying the
error position and message. `Validator.validate(document)` raises it on
invalid input; `validate_async()` provides the async equivalent.
`Validator.from_callable(callable, move_cursor_to_end=False)` adapts a
callable, and `DynamicValidator`, `ThreadedValidator`, and
`ConditionalValidator` provide dynamic, background, and filter-controlled
validation. A validation failure may move the cursor only when the selected
option requests it.

### Completion

`Completion(text, start_position=0, display=None, display_meta=None,
style="", selected_style="", type="", display_meta_style="")` describes
one replacement. Its `display_text`, `display_meta_text`, and
`new_completion_from_position()` properties are deterministic.

`Completer.get_completions(document, complete_event)` yields `Completion`
objects. `get_completions_async()` supports async completers. Implement
`WordCompleter`, `FuzzyWordCompleter`, `PathCompleter`,
`ExecutableCompleter`, `NestedCompleter`, `DeduplicateCompleter`,
`ThreadedCompleter`, `DynamicCompleter`, `ConditionalCompleter`, and
`merge_completers` with their documented filtering, case, filesystem, and
ordering behavior. Completion callbacks must receive a `Document` snapshot
and `CompleteEvent`; they must not mutate the buffer directly.

### Formatted text and styles

`HTML(value)` parses lightweight markup into styled text. Tags become class
names, nested tags combine classes, and `fg`/`bg` attributes become style
attributes. Values interpolated through `%` or `.format()` are escaped as
text. `ANSI(value)` parses ANSI SGR sequences into styled fragments and
represents unknown control characters with a safe replacement. Both objects
implement `__pt_formatted_text__`, `__repr__`, `%`, and `.format()`.

`FormattedText` is a list-like sequence of `(style, text)` fragments;
`to_formatted_text`, `merge_formatted_text`, `fragment_list_len`,
`fragment_list_width`, `fragment_list_to_text`, `split_lines`, and
`to_plain_text` convert and combine fragments while preserving order and
style boundaries. `PygmentsTokens` accepts `(token_tuple, text)` fragments;
Pygments-backed lexers are optional and loaded only when used.

`Style.from_dict(mapping)` and `Style(style_rules)` create immutable style
maps. `get_attrs_for_style_str()` resolves class names, ANSI colors, bold,
italic, underline, reverse, blink, strike, and foreground/background colors.
`merge_styles()` combines styles in order. Implement the style transformation
classes (`SwapLightAndDarkStyleTransformation`, `ReverseStyleTransformation`,
`SetDefaultColorStyleTransformation`, `AdjustBrightnessStyleTransformation`,
`DummyStyleTransformation`, `ConditionalStyleTransformation`, and
`DynamicStyleTransformation`) without mutating their inputs.

### Layout, widgets, and key bindings

`Layout(container, focused_element=None)` manages a tree of `Container`,
`Window`, and `UIControl` objects. Implement `walk`, focus navigation,
`current_buffer`, parent lookup, modal areas, and reset behavior. Dimension
objects (`Dimension`, `D`, `to_dimension`, `sum_layout_dimensions`, and
`max_layout_dimensions`) resolve preferred, minimum, and maximum sizes while
preserving integer bounds.

Provide the public containers and controls re-exported by
`prompt_toolkit.layout`: `HSplit`, `VSplit`, `FloatContainer`, `Float`,
`ConditionalContainer`, `DynamicContainer`, `ScrollablePane`, `Window`,
`BufferControl`, `SearchBufferControl`, `FormattedTextControl`,
`DummyControl`, `UIControl`, `UIContent`, and the margin classes. Rendering
must produce stable fragments for a fixed `Screen` size and focused layout.

Provide the widgets re-exported by `prompt_toolkit.widgets`, including
`TextArea`, `Label`, `Button`, `Frame`, `Shadow`, `Box`, line widgets,
`CheckboxList`, `RadioList`, `Checkbox`, `ProgressBar`, toolbars, dialogs,
`MenuContainer`, and `MenuItem`. Widgets expose their documented buffers,
controls, key bindings, focus behavior, and callbacks.

`KeyPress(key, data=None)` represents one decoded key. `KeyProcessor` queues
and dispatches key presses to `KeyBindings`. `KeyBindings.add(*keys,
filter=True, eager=False, is_global=False, save_before=False,
record_in_macro=True)` is a decorator for handlers; bindings are matched by
longest applicable prefix and preserve declaration order. Implement Emacs and
Vi editing modes, numeric arguments, macros, selection, clipboard, search,
digraphs, bracketed paste, and control-key behavior used by the public
shortcuts.

### Filters, event loop, and integrations

Implement the `Filter` protocol and the re-exported filter predicates, boolean
composition, `Condition`, `Always`, `Never`, `to_filter`, and `is_true`.
Filters may inspect the current application and must be evaluated at use time.

Implement `generator_to_async_generator`, `aclosing`,
`run_in_executor_with_context`, `call_soon_threadsafe`, traceback extraction,
and the input-hook context/selector APIs. Preserve context variables when
work is moved to an executor.

`prompt_toolkit.contrib.regular_languages.compile` and its grammar,
completion, lexer, and validation helpers provide the documented regular
language completion path. `contrib.telnet` and `contrib.ssh` are optional
network integrations; importing core modules must not require `asyncssh`.
`PygmentsLexer`, Pygments styles, and `PyperclipClipboard` likewise require
their optional packages only when those integrations are explicitly used.

## Terminal and Platform Contract

The core package must separate terminal-independent editing logic from native
I/O. A test or caller can supply `PipeInput` and `DummyOutput` and exercise a
complete prompt without a real terminal. A caller using default factories in
a redirected process must receive `PlainTextOutput` for output and a usable
POSIX input object or `DummyInput` for unavailable input, rather than a crash
caused solely by `isatty()` being false.

POSIX VT100 behavior includes raw/cooked mode restoration, terminal size
queries, cursor-position reports, color-depth selection, mouse and bracketed
paste escape sequences, and signal handling. Windows behavior includes the
Win32 console input/output and Windows 10 VT100 paths. Platform-specific code
must be guarded so importing the package on the other platform does not load
unavailable native symbols.

Do not claim that a headless Linux run verifies Windows console APIs, macOS
terminal behavior, SSH/telnet network sessions, system clipboard access, or a
focused interactive terminal. Those require a separately frozen platform
matrix and an approved verifier adapter.
