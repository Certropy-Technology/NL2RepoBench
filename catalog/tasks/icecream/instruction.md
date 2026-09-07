# Project Description

Create an installable Python package named `icecream` that provides the public
debug-printing helpers from the pinned upstream revision. The package must be
usable without a terminal, display server, network service or process-global
test fixture. Verification uses a deterministic mocked output sink.

# Natural Language Instruction

Create the `icecream` Python package from an empty `workspace/`. Implement the
public debugger object and its module-level configuration helpers described in
this document. The package must support four concrete capability groups:

1. Debug calls accept one or more Python values, emit a formatted diagnostic
   through the configured callback, and return the original argument or tuple.
2. Formatting helpers represent strings, newlines, literal expressions, pairs,
   and optional ANSI colors without requiring a terminal.
3. Configuration controls output callbacks, prefixes, enabled state, context
   display, and singledispatch registrations deterministically.
4. Installation helpers add and remove a named builtin debugger and report a
   missing installed name using the documented exception behavior.

Keep the root import path `icecream` and the public `ic` object compatible with
ordinary use. Do not add a CLI, network client, service, process-global test
fixture, or output side effect during import.

# Supports

- Support Python 3.8 and newer and install from an empty workspace with no
  runtime network access.
- Preserve the public package exports, version metadata, and module entry
  points from the exact source revision recorded in `task.toml`.
- Keep debugging disabled/enabled state, output configuration, prefix
  formatting and callback behavior deterministic.
- Debug calls return the single argument unchanged and return a tuple for
  multiple arguments while sending formatted output only through the selected
  output callback.

# Project Directory Structure

```text
workspace/
├── pyproject.toml
├── README.md
└── icecream/
    ├── __init__.py
    └── icecream.py
```

`icecream/__init__.py` is the public re-export entry point. The implementation
module contains the debugger, formatting helpers, callback configuration, and
version metadata. The project must install from `workspace/` with the normal
Python build frontend; no evaluator, verifier, or fixture files belong in the
generated project.

# API Usage Guide

The public module is imported with `from icecream import ic, configureOutput`.
The following signatures are part of the contract:

```python
ic(*args: object) -> object | tuple[object, ...]
configureOutput(outputFunction=None, argsToStringFunction=None,
                prefix=None, includeContext=False,
                suppressWarnings=False) -> None
configurePrefix(prefix: str | callable) -> None
enable() -> None
disable() -> None
install() -> None
uninstall() -> None
```

`ic(value)` returns that value, while `ic(first, second)` returns
`(first, second)` in the same order. A disabled debugger returns values without
calling the output callback. Prefix callables are evaluated for each enabled
call, and callback configuration remains local to the debugger state.

```python
from icecream import ic

result = ic("ready")
pair = ic(1, 2)
assert result == "ready" and pair == (1, 2)
```

```python
from icecream import argumentToString, format, format_pair, isLiteral

argumentToString("line\ntext", None)
format_pair("count", 3)
format(3)
isLiteral("name")
```

The package must expose the standard `ic` debugger and its configuration
helpers, including `configureOutput`, `configurePrefix`, `enable`, `disable`,
`install`, `uninstall`, `format`, `format_pair`, `colorize`, `argumentToString`,
`isLiteral`, and the public version/re-export metadata. Preserve the callable
prefix and formatter hooks, including singledispatch registration and
unregistration.

The scored behavior covers these deterministic contracts:

- version and non-empty public re-exports;
- stable pretty-printing of simple values, strings containing newlines and
  literal recognition;
- `format` and `format_pair` output through a mocked callback without terminal
  I/O, including aligned string values and pure colorization;
- `ic` return values for one and multiple arguments;
- disabled debug calls as output-free pass-throughs and `enable` restoring the
  configured callback;
- output configuration, prefix evaluation on each call, and validation of
  required changes;
- singledispatch registration/unregistration;
- prefix-line indentation helpers;
- installing and uninstalling a custom builtin name, including the missing-name
  error contract; and
- deterministic debugger formatting for one or several simple values.

# Implementation Notes

Do not write to stdout/stderr as an import side effect, require a real terminal,
or use a network/GUI backend to satisfy the debugger contract. Keep output
callback invocation and return-value behavior compatible with the public API.
The verifier may replace output callbacks and invokes candidate behavior in a
separate child process; hidden verifier code and fixtures are not part of the
candidate workspace.

# Examples

The ordinary integration path is to import `ic`, call it around a value, and
use the returned value in the surrounding expression. Configuration can replace
the output sink with an in-memory list for a non-terminal application.

```python
messages = []
ic.configureOutput(outputFunction=messages.append)
value = ic("payload")
assert value == "payload"
```

```python
ic.disable()
assert ic("silent") == "silent"
ic.enable()
```

# Error Handling and Boundary Conditions

- `configureOutput` must reject invalid non-callable output or formatter
  settings according to the public exception contract instead of silently
  replacing them.
- `uninstall()` reports the missing builtin name when `install()` has not
  installed one; it must not modify unrelated builtins.
- A prefix string remains stable, while a prefix callable is evaluated on each
  call. Newline-containing values retain their content and receive the
  documented line indentation.
- Formatting and disabled calls must not write directly to stdout or stderr.
  All execution is deterministic under the selected callback and has no network
  or terminal dependency.
