# Build `prompt_toolkit`

Create an installable Python package named `prompt_toolkit`. This task freezes
a deterministic, headless compatibility slice of prompt_toolkit 3.0.53. It is
a library task, not a terminal-rendering task: implement the normal public
APIs below without adding evaluator-specific entry points or depending on an
already installed copy of the package.

## Supports

- Support CPython 3.10 and newer. Use a `src/prompt_toolkit/` package layout
  and a `pyproject.toml` such that `python -m pip install .` works from an
  empty workspace when build dependencies are already installed.
- The distribution name is `prompt_toolkit` and its version is `3.0.53`.
  `prompt_toolkit.__version__` is exactly `"3.0.53"` and
  `prompt_toolkit.VERSION` is exactly `(3, 0, 53)`.
- Declare `wcwidth>=0.1.4` as the runtime dependency. Include package
  metadata, a BSD-3-Clause license notice, a README, and
  `prompt_toolkit/py.typed`.
- Core imports and the behaviors below must work without a TTY, network,
  system clipboard, or platform console APIs. Do not require evaluator tests
  to import or install the package.

## Root API

The root module has this ordered `__all__` list and exposes every listed name:

```python
[
    "Application", "prompt", "choice", "PromptSession",
    "print_formatted_text", "HTML", "ANSI", "__version__", "VERSION",
]
```

The following class names must be importable from their normal modules:

```python
from prompt_toolkit.document import Document
from prompt_toolkit.buffer import Buffer, EditReadOnlyBuffer
from prompt_toolkit.completion import Completion, CompleteEvent, WordCompleter
from prompt_toolkit.completion import NestedCompleter, merge_completers
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.clipboard import ClipboardData, InMemoryClipboard
from prompt_toolkit.selection import SelectionState, SelectionType
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPress, KeyProcessor
from prompt_toolkit.keys import Keys
from prompt_toolkit.application.current import set_app
from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.layout import Layout, Window
from prompt_toolkit.output import DummyOutput
```

`Application`, `PromptSession`, `prompt`, `choice`, and
`print_formatted_text` must remain callable/importable as root APIs. This
headless slice does not call their interactive rendering paths.

## Documents and Buffers

`Document(text="", cursor_position=None, selection=None)` is immutable.
When omitted, `cursor_position` is `len(text)`; positions are zero-based and
may equal `len(text)`. It exposes `text`, `cursor_position`, `selection`,
`current_char`, `char_before_cursor`, `text_before_cursor`, `text_after_cursor`,
`current_line_before_cursor`, `current_line_after_cursor`, `current_line`,
`lines`, `line_count`, `cursor_position_row`, and `cursor_position_col`.
`lines` retains a trailing empty element for text ending in a newline.

`find(sub, include_current_position=False)` reports a relative forward offset
or `None`; `find_backwards(sub)` reports a relative backward offset or `None`.
`get_word_before_cursor()` returns the alphanumeric/underscore word immediately
before the cursor. `translate_index_to_position(index)` returns zero-based
`(row, column)`, and `translate_row_col_to_index(row, column)` clamps to valid
line and column bounds.

`Buffer` owns mutable text and cursor state. `insert_text`, `cursor_left`,
`cursor_right`, `delete_before_cursor`, `save_to_undo_stack`, `undo`, and
`redo` update text and cursor consistently. `delete_before_cursor(count)`
returns the removed string. `Buffer(read_only=True)` raises
`EditReadOnlyBuffer` for mutation. `apply_completion(completion)` replaces the
text selected by the completion's negative `start_position` and puts the
cursor after inserted completion text.

For example, starting with `"some_text"`, moving left three places, moving
right one place, and inserting `"A"` produces `"some_teAxt"`; deleting two
characters before that cursor produces `"some_txt"`. Saving `"abcd"`, moving
left twice, and inserting `"XY"` produces `"abXYcd"`; undo restores
`"abcd"` and redo restores `"abXYcd"`.

## Completion

`Completion(text, start_position=0, display=None, display_meta=None,
style="", selected_style="")` has `text`, `start_position`, `style`,
`selected_style`, `display_text`, and `display_meta_text`. `start_position`
must be non-positive. `new_completion_from_position(position)` returns the
remaining replacement text with default style fields while preserving display
and display metadata.

`WordCompleter(words, ignore_case=False, sentence=False, match_middle=False,
...)` yields `Completion` values in supplied word order. It normally matches
the word before the cursor, optionally case-insensitively; with
`sentence=True`, it matches all text before the cursor. `NestedCompleter`
created from a nested dictionary yields keys at the active nesting level in
dictionary insertion order. `merge_completers(..., deduplicate=True)` preserves
the first completion yielding each resulting text.

The words `alpha`, `Alpine`, `beta`, `alphabet` yield `alpha` and `alphabet`
for `"a"`, only `Alpine` for `"A"` by default, and `alpha`, `Alpine`,
`alphabet` for `"A"` with `ignore_case=True`. A sentence completer with
`"show version"`, `"show value"`, `"exit"` returns the first two for
`"show v"`.

## History, Clipboard, and Validation Data

`InMemoryHistory` loads strings newest first through its async `load()`
generator and returns loaded strings oldest first through `get_strings()`.
`append_string` records a new entry.

`ClipboardData(text="", type=SelectionType.CHARACTERS)` stores `text` and a
`SelectionType`. `InMemoryClipboard` is a bounded kill ring: `set_data` adds
the newest item, `set_text` adds character data, `get_data` returns the newest
item, and `rotate` advances to the next stored item. `SelectionType` includes
`CHARACTERS`, `LINES`, and `BLOCK`. `SelectionState(position, type)` stores
the original position and type; `enter_shift_mode()` sets `shift_mode`.

`ValidationError(cursor_position=0, message="")` exposes its cursor position
and message. `Validator.from_callable(func, error_message=...,
move_cursor_to_end=True)` rejects a false callable result with a
`ValidationError` whose cursor position is the end of the document.
`Buffer.validate(set_cursor=True)` returns `False`, stores that error, and
moves its cursor to the reported position; it returns `True` with no stored
error when validation succeeds.

## Headless Key Bindings

`KeyBindings.add(*keys, filter=True, eager=False, is_global=False,
save_before=..., record_in_macro=True)` registers handlers. `KeyProcessor`
receives `KeyPress` values through `feed()` and dispatches them with
`process_keys()`. A matching longer active sequence delays a shorter prefix;
when a later nonmatching key arrives, dispatch the shorter prefix before
processing the later key. Exact longer matches win when supplied. `Keys.Any`
matches one arbitrary key in a sequence.

This behavior must work with an `Application(Layout(Window()),
input=create_pipe_input(), output=DummyOutput())` used only as a headless
state holder. For bindings `ControlX`, `ControlX-ControlC`, `ControlD`, and
`ControlSquareClose-Any`, a lone `ControlX` remains pending; a following
`ControlD` dispatches `ControlX` then `ControlD`; `ControlX-ControlC`
dispatches only the longer handler; and `ControlSquareClose` followed by `z`
dispatches the wildcard handler with `z` data.

## Excluded Interactive Behavior

Do not assume this task verifies terminal escape rendering, raw/cooked mode
restoration, terminal sizing, mouse input, native Windows input/output,
system clipboard integration, SSH/telnet, or a live prompt loop. Those
behaviors require a separately frozen TTY/platform adapter and are not hidden
requirements here. The evaluator runs the listed API calls in an isolated
child process with controlled `PipeInput` and `DummyOutput`; it does not score
renderer bytes or OS-specific interactive behavior.
