# prompt-toolkit

## Project Description

Build an installable `prompt-toolkit` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution identity: `prompt-toolkit`; public import package begins at `prompt_toolkit`.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `Build `prompt_toolkit`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `Root API`: preserve the documented object or module behavior, including state and side effects.
3. `Documents and Buffers`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `Completion`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- CPython 3.12.14 on the pinned Linux image.
- Distribution identity: `prompt-toolkit`; public import package begins at `prompt_toolkit`.
- Install from the workspace with `python -m pip install .`; do not download packages during evaluation.
- Declared build/runtime packages are supplied by the frozen evaluation image: `setuptools==80.10.2`, `wcwidth==0.8.1`
- Build metadata and package data must be present in the workspace and agree with the public import paths below.
- Agent, candidate, evaluator, Oracle, and control execution are network-isolated. Do not access GitHub, package registries, DNS, databases, or external services at runtime.
- Use deterministic local inputs. Do not rely on the current wall clock, host-specific absolute paths, undeclared environment variables, or an installed copy of the target package.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── an/
│   ├── __init__.py
│   └── (public modules documented in API Usage Guide)
```

The tree lists agent-owned public project files only. Add additional public modules when required by the API Usage Guide, but keep their import paths consistent with package metadata. Do not create evaluator-only files, hidden fixtures, or private reports in the generated project.

## API Usage Guide

The following is the task-specific public contract recovered from the local instruction and inventory. For every function, class, method, constant, export, and command named below, preserve its complete signature, accepted input domain, return type and shape, ordering, determinism, state/side effects, exceptions, and examples. When the source contract gives an optional argument or a compatibility alias, it is part of the required surface.

# Build `prompt_toolkit`

Create an installable Python package named `prompt_toolkit`. This task freezes
a deterministic, headless compatibility slice of prompt_toolkit 3.0.53. It is
a library task, not a terminal-rendering task: implement the normal public
APIs below without adding evaluator-specific entry points or depending on an
already installed copy of the package.


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

## Implementation Notes

- Keep the root exports and module paths stable after installation; do not make behavior depend on the repository's current directory.
- Preserve explicit ordering guarantees. When the contract does not promise an order, do not introduce a new observable order accidentally.
- Propagate documented exceptions and avoid replacing them with generic errors. Validate malformed, empty, boundary, and repeated inputs as described by the API contract.
- Keep filesystem, process, terminal, and resource effects bounded and local. Close files and other resources on both success and failure.
- Do not copy an upstream checkout, implementation source, or evaluation-only material into the generated project. Implement the public behavior from this specification.

## Examples

The examples below are retained from the local task specification. They are starting points for ordinary calls and boundary/error behavior; their exact output and exception semantics remain governed by the API Usage Guide.

### Example 1: ordinary usage
```text
[
    "Application", "prompt", "choice", "PromptSession",
    "print_formatted_text", "HTML", "ANSI", "__version__", "VERSION",
]
```

### Example 2: ordinary usage
```text
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

### Example 3: boundary or error behavior
```text
[
    "Application", "prompt", "choice", "PromptSession",
    "print_formatted_text", "HTML", "ANSI", "__version__", "VERSION",
]
```

### Example 4: boundary or error behavior
```text
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


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
