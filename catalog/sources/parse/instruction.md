# parse

## Project Description

Build an installable `parse` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution identity: `parse`; public import package begins at `parse`.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `parse.parse`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `parse.search`: preserve the documented object or module behavior, including state and side effects.
3. `parse.findall`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `parse.compile` and `parse.Parser`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- CPython 3.12.14 on the pinned Linux image.
- Distribution identity: `parse`; public import package begins at `parse`.
- Install from the workspace with `python -m pip install .`; do not download packages during evaluation.
- Declared build/runtime packages are supplied by the frozen evaluation image: `setuptools==80.10.2`, `wheel==0.45.1`
- Build metadata and package data must be present in the workspace and agree with the public import paths below.
- Agent, candidate, evaluator, Oracle, and control execution are network-isolated. Do not access GitHub, package registries, DNS, databases, or external services at runtime.
- Use deterministic local inputs. Do not rely on the current wall clock, host-specific absolute paths, undeclared environment variables, or an installed copy of the target package.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── text/
│   ├── __init__.py
│   └── (public modules documented in API Usage Guide)
```

The tree lists agent-owned public project files only. Add additional public modules when required by the API Usage Guide, but keep their import paths consistent with package metadata. Do not create evaluator-only files, hidden fixtures, or private reports in the generated project.

## API Usage Guide

The following is the task-specific public contract recovered from the local instruction and inventory. For every function, class, method, constant, export, and command named below, preserve its complete signature, accepted input domain, return type and shape, ordering, determinism, state/side effects, exceptions, and examples. When the source contract gives an optional argument or a compatibility alias, it is part of the required surface.

## `parse.parse`

```python
parse(format, string, extra_types=None, evaluate_result=True,
      case_sensitive=False)
```

Match `format` against the whole `string`. Both required arguments are
strings. Return `None` when the text does not match. Otherwise return a
`Result`; when `evaluate_result=False`, return a `Match` whose
`evaluate_result()` method produces that same `Result`.

Literal text is escaped: regular-expression metacharacters such as `?`, `|`,
`[`, `]`, `(`, and `*` have no special meaning. `{{` and `}}` denote literal
braces. Matching is case-insensitive by default and case-sensitive when
requested. Matching and extracted values preserve Unicode and newlines.

Fields use `{}`, `{name}`, or `{0}` syntax. Unnamed and numeric fields are
placed in `Result.fixed` in field order. Named fields are placed in
`Result.named`. A format may mix both kinds. Repeating a named field requires
the same source text each time; a different repeated value does not match.
Dot-separated names such as `{user.name}` remain flat dictionary keys.
Bracket paths such as `{user[name]}` create nested dictionaries.

The following type codes are required:

| Code | Accepted text | Result value |
| --- | --- | --- |
| absent or `s` | any non-empty text | `str` |
| `w` | one or more word characters | `str` |
| `W` | one or more non-word characters | `str` |
| `d` | signed decimal or `0b`/`0o`/`0x` integer | `int` |
| `b`, `o`, `x` | binary, octal, hexadecimal integer | `int` |
| `f`, `F`, `e`, `g` | signed decimal floating point | `float`, except `F` returns `Decimal` |
| `%` | decimal percentage ending in `%` | fraction as `float` |
| `l` | one or more ASCII letters | `str` |

For text fields, a width (`{:4}`) is a minimum unless precision is also
present. Precision (`{:.4}`) is a maximum. Equal width and precision
(`{:4.4}`) therefore require exactly four characters. Adjacent fixed-width
fields split deterministically. Numeric zero padding such as `{:02d}` is
supported.

Alignment markers `<`, `>`, and `^` strip matching padding from the extracted
value. A character before the marker is the fill character, for example
`{:.>}`. Sign flags on numeric fields are accepted but do not require a sign.

## `parse.search`

```python
search(format, string, pos=0, endpos=None, extra_types=None,
       evaluate_result=True, case_sensitive=False)
```

Return the first match anywhere in `string`, or `None`. Search starts at
`pos`; `endpos` is an exclusive upper bound. Result evaluation, case handling,
field conversion, and result shape are the same as for `parse()`.

## `parse.findall`

```python
findall(format, string, pos=0, endpos=None, extra_types=None,
        evaluate_result=True, case_sensitive=False)
```

Return an iterable of successive, non-overlapping matches in source order.
The range and case options have the same meaning as in `search()`. Each item is
a `Result`, or a `Match` when evaluation is delayed. An empty match set is an
empty iterable.

## `parse.compile` and `parse.Parser`

```python
compile(format, extra_types=None, case_sensitive=False) -> Parser
Parser(format, extra_types=None, case_sensitive=False)
```

Create a reusable parser. `Parser.parse(string, evaluate_result=True)`,
`Parser.search(string, pos=0, endpos=None, evaluate_result=True)`, and
`Parser.findall(string, pos=0, endpos=None, evaluate_result=True)` follow the
function contracts above. `Parser.format` retains the original format string.
`fixed_fields` lists the zero-based positions of fixed fields among all fields
in the format, and `named_fields` lists named fields in format order.

Malformed fields and an unknown type code raise `ValueError`. Compiling the
same repeated field name with incompatible type codes raises
`RepeatedNameError`, a `ValueError` subclass.

## `parse.Result`

```python
Result(fixed, named, spans)
```

`fixed` is exposed as a tuple and `named` as a dictionary. Integer and slice
subscription reads `fixed`; string subscription reads `named`. Missing integer
indexes raise `IndexError`, and missing names raise `KeyError`. Membership
tests dictionary keys only. Results from parsing also expose `spans`, mapping
each fixed index or named key to the half-open `(start, end)` source range.


The parser should translate the supported format grammar into safe matching
logic and then convert captured text. It must treat format literals as
literals, anchor `parse()` to the complete input, preserve source order for
`findall()`, and avoid zero-length iteration loops. Public behavior, not a
particular regular-expression construction, is graded.

```python
from parse import compile, findall, parse, search

assert parse("hello {}", "hello world").fixed == ("world",)
assert parse("{n:d}", "0x10").named == {"n": 16}
assert search("age: {:d}", "name: Ada; age: 42").fixed == (42,)
assert [r.fixed[0] for r in findall("<{}>", "<a><b>")] == ["a", "b"]
assert compile("{name:w}:{score:03d}").parse("Ada:007").named == {
    "name": "Ada",
    "score": 7,
}
```

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
parse(format, string, extra_types=None, evaluate_result=True,
      case_sensitive=False)
```

### Example 2: ordinary usage
```text
search(format, string, pos=0, endpos=None, extra_types=None,
       evaluate_result=True, case_sensitive=False)
```

### Example 3: boundary or error behavior
```text
findall(format, string, pos=0, endpos=None, extra_types=None,
        evaluate_result=True, case_sensitive=False)
```

### Example 4: boundary or error behavior
```text
compile(format, extra_types=None, case_sensitive=False) -> Parser
Parser(format, extra_types=None, case_sensitive=False)
```


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
