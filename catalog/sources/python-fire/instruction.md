# Project Description

Create the installable Python package `fire` from the exact revision recorded
in `task.toml`. The scored contract is a deterministic, noninteractive CLI
slice built around `fire.Fire`: functions, classes, dictionaries and sequences
must be traversable from command-line arguments and produce stable values,
help text and errors.

# Supports

- Support Python 3.7 and newer and install offline from an empty workspace.
- Preserve the `fire.Fire` export, version metadata, `python -m fire` entry
  behavior and the standard `termcolor`-backed formatting dependency.
- Do not start a REPL, pager, network request or interactive terminal during
  the scored behavior.

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
