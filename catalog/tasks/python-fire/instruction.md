# Project Description

Create the installable Python package `fire` from the exact revision recorded
in `task.toml`. The scored contract is a deterministic, noninteractive CLI
slice built around `fire.Fire`: functions, classes, dictionaries and sequences
must be traversable from command-line arguments and produce stable values,
help text and errors.

## Supports

- Support Python 3.7 and newer and install offline from an empty workspace.
- Preserve the `fire.Fire` export, version metadata, `python -m fire` entry
  behavior and the standard `termcolor`-backed formatting dependency.
- Do not start a REPL, pager, network request or interactive terminal during
  the scored behavior.

## Natural Language Instruction

Create the `fire` Python project from an empty `workspace/`. Implement the
public `fire.Fire` entry point and the `python -m fire` command as a real,
deterministic command-line traversal library. The implementation must:

1. Traverse functions, classes, dictionaries, and sequences using positional
   arguments and named flags.
2. Convert command-line text to booleans, integers, lists, strings, and
   Unicode values using the documented Fire conventions.
3. Preserve class construction, method dispatch, varargs, help generation,
   and stable errors for missing or unknown commands.
4. Expose package metadata and normal import behavior without an interactive
   shell, network, clock, or external service.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── LICENSE
├── fire/
│   ├── __init__.py
│   ├── __main__.py
│   ├── core.py
│   ├── formatting.py
│   ├── inspectutils.py
│   ├── parser.py
│   └── trace.py
└── README.md
```

`fire/__init__.py` is the import root and exports `Fire` and version
information. `fire/__main__.py` is the `python -m fire` entry point. The
remaining modules may be organized differently internally, but every public
entry described below must remain importable from its documented path.

# API Usage Guide

The verifier supplies an allowlisted JSON fixture name and an argv list to a
candidate-side adapter. The adapter constructs these in-process fixtures:

- an `add(alpha, beta=2, *rest, gamma=False)` function;
- a typed echo function;
- a calculator class with an offset constructor and `double`/`join` methods;
- a mapping with nested Unicode values;
- a numeric sequence; and
- a function that raises `ValueError`.

The package must support positional and named flags, `--name=value` syntax,
varargs, boolean flags, integer/list/Unicode parsing, class initialization
flags, class method traversal, dictionary and list lookup, stable exception
exit behavior, missing-required-argument errors, unknown-command usage errors,
and deterministic help sections for the add function. Single scalar results,
structured JSON-safe observations, stdout and stderr text, and exit codes must
match the public behavior documented by the slice.

The adapter never accepts Python source, import paths, filesystem paths,
callables or shell commands from the request. The candidate still implements
the normal public Fire API; the adapter is only a boundary for verification.

# Implementation Notes

Keep help and error output deterministic under the verifier's fixed locale,
timezone, terminal and color environment. Do not satisfy the task with a
hard-coded response table or by importing the private verifier. The full
upstream Hypothesis fuzz suite, IPython REPL and arbitrary callback-object
surface are outside this frozen denominator and are not implied by this task.

## Examples

```python
from fire import Fire

def add(alpha, beta=2):
    return alpha + beta

Fire(add, command=['3', '--beta=4'])
```

```console
$ python -m fire my_module add 3 --beta=4
7
```

```console
$ python -m fire my_module add --help
NAME
    add
```

## Error Handling and Boundary Conditions

Required positional arguments must produce a nonzero result and an actionable
error rather than an uncaught implementation traceback. Unknown commands and
invalid flags must also fail deterministically. Dictionary and sequence
traversal must report missing keys or indexes without reading a filesystem.
Unicode values are ordinary strings, and help output must not depend on color
support or terminal width.

The command parser must preserve the distinction between a positional value,
an option value, and a command name. Repeated options and varargs retain their
declared order, while a boolean flag without an explicit value means `True`.
Help describes the selected callable and does not execute it as a side effect.
