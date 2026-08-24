# Project Description

Create an installable Python package named `icecream` that provides the public
debug-printing helpers from the pinned upstream revision. The package must be
usable without a terminal, display server, network service or process-global
test fixture. Verification uses a deterministic mocked output sink.

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

# API Usage Guide

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
