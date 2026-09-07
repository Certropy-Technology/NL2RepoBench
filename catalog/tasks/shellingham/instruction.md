# Project Description

Implement the `shellingham` Python package (version 1.5.4) from an empty
workspace. It detects the interactive shell that owns a process by examining
the POSIX process tree, with a platform dispatch entry point for supported
operating systems. The package must be installable with `pip install .` and
must not require network access at runtime.

## Natural Language Instruction

Create `shellingham` from an empty workspace as a complete installable python project. Implement
the public operations, data or state behavior, input validation, deterministic ordering, and
error contracts documented below. Keep package metadata, root exports, module imports, and any
subpath entry points consistent across files. Implement the behavior rather than hard-coding the
examples, and do not retrieve or copy a reference implementation.

The finished repository must install from its root, expose every documented API family, preserve
the specified side effects and resource lifecycle, and remain usable in a fresh process.

## Supports

- Package/distribution name: `shellingham`. Primary import or package entry: `shellingham`.
- CPython 3.12.11 on debian-12-amd64 with pip.
- Install from `workspace/` using `python -m pip install .`.
- Declared dependency closure: setuptools==80.10.2, wheel==0.45.1. Standard-library modules are not dependencies.
- Build requirements are supplied before execution; do not add undeclared dependencies,
  registry overrides, download hooks, or source-fetch steps.
- Agent, candidate, verifier, Oracle, and controls use `network_mode=no-network`. Runtime access
  to GitHub, PyPI, npm, the Go proxy, DNS, and external services is forbidden.
- The declared test framework is `pytest`. A fixed collection
  contains `24` cases when that value is frozen in metadata;
  test implementation details are not part of the package surface.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── shellingham/
│   ├── __init__.py
│   ├── _core.py
│   └── posix/
│       ├── __init__.py
│       ├── _core.py
│       ├── proc.py
│       └── ps.py
└── README.md
```

This is the required public project shape. Additional implementation modules are allowed only
when they support the documented API; evaluation, source-fetch, and private runtime files are
not agent-owned project files.

## API Usage Guide

### `shellingham.detect_shell(pid=None, max_depth=10)`

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

### `shellingham.ShellDetectionFailure`

This exception is re-exported at the top level and subclasses
`EnvironmentError`. It is the failure type for an otherwise supported platform
when a process tree cannot provide a shell result.

### `shellingham.posix.get_shell(pid=None, max_depth=10)`

This POSIX-specific entry point has the same input and return shape as
`detect_shell`. It inspects at most `max_depth` process records and returns
the first matching shell tuple. Shell names include Bourne-style shells such
as `sh`, `bash`, `dash`, and `ash`, C shells, common alternatives such as
`zsh` and `fish`, Microsoft shell names, and the documented exotic names
`elvish`, `xonsh`, and `nu`. A command beginning with `-` is treated as a
login shell. Interpreter-launched `xonsh` is recognized when an argument is an
existing xonsh script.

### `shellingham.posix._core.Process(args, pid, ppid)`

`Process` is a named-tuple-like record with fields `args`, `pid`, and `ppid`.
`args` is a tuple of command-line strings. The process iterators yield these
records from the requested process toward its parents.

### POSIX process iterators

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

## Implementation Notes

- Keep the package importable on Linux without invoking `ps` or reading a
  process tree at import time.
- Preserve the exact tuple and exception contracts above, including string
  process IDs returned by POSIX helpers.
- Do not add runtime dependencies. Build metadata may use setuptools and
  wheel, which are already available in the task image.
- Keep process inspection bounded by `max_depth`; do not create persistent
  child processes or depend on external services.
- Process data and filesystem inputs should be handled deterministically and
  independently of the machine's current interactive shell where the API
  permits.

Use the public language semantics described by each API family. Keep repeated calls deterministic
unless state mutation is explicitly part of the contract. Public re-exports and declarations must
match runtime behavior, and installation must not rely on a repository checkout or network access.

## Examples

The API-specific examples above are normative demonstrations of ordinary behavior. These four
local snippets also provide ordinary and boundary-oriented calls without external services:

```python
import shellingham

try:
    shell_name, shell_path = shellingham.detect_shell()
except shellingham.ShellDetectionFailure:
    shell_name, shell_path = "unknown", ""
```

```python
import shellingham
# Invoke a documented API using an empty or boundary input.
```

```python
import shellingham
print(shellingham)
```

```python
import shellingham
# Invoke a documented API using an empty or boundary input.
```

## Error Handling and Boundary Conditions

Empty values, malformed values, unsupported types, exhausted inputs, invalid options, and missing
local resources must follow the API-specific contracts above. Preserve documented exception types
and messages where they are stated. Do not silently coerce an unsupported value merely to produce
a result, and do not mutate caller-owned data unless the relevant API explicitly promises it.

All filesystem, process, terminal, clock, randomness, and service interactions are forbidden unless
the API guide explicitly includes that local behavior. Even for an API that models remote or async
work, evaluation must remain bounded, deterministic, and disconnected from public networks.
