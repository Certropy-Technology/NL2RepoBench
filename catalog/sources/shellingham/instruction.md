# Project Description

Implement the `shellingham` Python package (version 1.5.4) from an empty
workspace. It detects the interactive shell that owns a process by examining
the POSIX process tree, with a platform dispatch entry point for supported
operating systems. The package must be installable with `pip install .` and
must not require network access at runtime.

# Supports

- Python 3.12 on a Linux/POSIX environment.
- The top-level `shellingham` package and its public `posix` submodule.
- Deterministic process records represented by
  `shellingham.posix._core.Process`.
- POSIX `/proc` parsing with a `ps` fallback, bounded by a caller-provided
  maximum depth.

# API Usage Guide

## `shellingham.detect_shell(pid=None, max_depth=10)`

Import this function from `shellingham`. `pid` accepts an integer or a string
process identifier; when it is `None`, use the current process. `max_depth` is
the maximum number of parent records to inspect. Return a two-item tuple
`(name, executable)` where both values are strings. The name is lower-cased and
the executable is the path or command that identified the shell. A shell
found through a login-shell command uses the `SHELL` environment variable
when it is set. Raise `shellingham.ShellDetectionFailure` when no compatible
process source is available or no shell is found. Raise `RuntimeError` when
the current operating-system implementation is unavailable.

Example:

```python
import shellingham

try:
    shell_name, shell_path = shellingham.detect_shell()
except shellingham.ShellDetectionFailure:
    shell_name, shell_path = "unknown", ""
```

## `shellingham.ShellDetectionFailure`

This exception is re-exported at the top level and subclasses
`EnvironmentError`. It is the failure type for an otherwise supported platform
when a process tree cannot provide a shell result.

## `shellingham.posix.get_shell(pid=None, max_depth=10)`

This POSIX-specific entry point has the same input and return shape as
`detect_shell`. It inspects at most `max_depth` process records and returns
the first matching shell tuple. Shell names include Bourne-style shells such
as `sh`, `bash`, `dash`, and `ash`, C shells, common alternatives such as
`zsh` and `fish`, Microsoft shell names, and the documented exotic names
`elvish`, `xonsh`, and `nu`. A command beginning with `-` is treated as a
login shell. Interpreter-launched `xonsh` is recognized when an argument is an
existing xonsh script.

## `shellingham.posix._core.Process(args, pid, ppid)`

`Process` is a named-tuple-like record with fields `args`, `pid`, and `ppid`.
`args` is a tuple of command-line strings. The process iterators yield these
records from the requested process toward its parents.

## POSIX process iterators

`shellingham.posix.proc.detect_proc()` returns `"stat"` for Linux-style
`/proc/<pid>/stat` or `"status"` for BSD-style `/proc/<pid>/status`, and
raises `ProcFormatError` for an unsupported layout.
`shellingham.posix.proc.iter_process_parents(pid, max_depth=10)` parses the
selected proc format and yields at most `max_depth` records. Its command line
parser treats the trailing NUL in `/proc/<pid>/cmdline` as a separator.

`shellingham.posix.ps.iter_process_parents(pid, max_depth=10)` invokes the
fixed `ps -ww -o pid= -o ppid= -o args=` query, ignores malformed output lines,
and follows at most `max_depth` records. It raises `PsNotAvailable` when `ps`
is absent. An empty process list is represented by an empty iterator.

# Implementation Notes

- Keep the package importable on Linux without invoking `ps` or reading a
  process tree at import time.
- Preserve the exact tuple and exception contracts above, including string
  process IDs returned by POSIX helpers.
- Do not add runtime dependencies. Build metadata may use setuptools and
  wheel, which are already available in the task image.
- Keep process inspection bounded by `max_depth`; do not create persistent
  child processes or depend on external services.
- The verifier supplies controlled process data and filesystem fixtures, so
  implementation behavior must be deterministic and independent of the
  machine's current shell.
