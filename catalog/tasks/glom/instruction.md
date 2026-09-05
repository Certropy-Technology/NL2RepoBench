# Build `glom`

Create a complete, installable Python package named `glom` from an empty
workspace. Implement the frozen upstream glom behavior described by the public
contracts below; do not copy the upstream source tree or tests.

## Project Description

glom is a declarative data transformation library. A target value is evaluated
against a specification (`spec`) to select nested values, construct mappings
and sequences, call functions, match data, mutate mappings, and process
iterables. The package is pure Python and must work without network access or
external services after installation.

## Supports

- CPython 3.12 on Linux amd64.
- An installable `glom` package with a deterministic `__version__` matching
  the distribution metadata for this task (`25.12.1.dev0`).
- Root imports and public aliases for the core API in the frozen revision:
  `glom`, `T`, `S`, `A`, `ROOT`, `UP`, `SKIP`, `STOP`, `Path`, `Spec`, `Val`,
  `Call`, `Invoke`, `Coalesce`, `Ref`, `Vars`, `Pipe`, `Fill`, `Inspect`,
  `Match`, `Regex`, `And`, `Or`, `Not`, `Optional`, `Required`, `Switch`,
  `Check`, `Iter`, `Sum`, `Fold`, `Flatten`, `Merge`, `flatten`, `merge`,
  `assign`, `delete`, `Assign`, `Delete`, `Glommer`, `register`, and
  `register_op`, plus their documented exception classes.
- Deterministic local behavior only. Do not use subprocesses, network calls,
  mutable environment state, or random values in the implementation.

## Natural Language Instruction

Create the installable `glom` package from an empty workspace. Implement the
root exports and all evaluation, specification, matching, mutation, iteration,
registration, and exception behavior listed in the API guide.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
└── glom/
    ├── __init__.py
    ├── core.py
    ├── matching.py
    ├── streaming.py
    ├── mutation.py
    └── glommer.py
```

The modules above represent the public import surface; internal organization
may vary while preserving every documented import and root re-export. Do not
include verifier or hidden-test files.

## Examples

```python
from glom import glom
glom({'name': 'Ada'}, 'name')
```

```python
from glom import T, Spec
glom({'user': {'name': 'Ada'}}, Spec({'name': ('user', T)}))
```

## Error Handling and Boundary Conditions

Preserve missing-path, default, `SKIP`/`STOP`, matching failure, mutation,
iterator exhaustion, callable, and registration error contracts. Evaluation is
deterministic, bounded, and offline; do not depend on time or network state.

## API Usage Guide

### Core evaluation

`glom(target, spec, **kwargs)` returns a value produced by evaluating `spec`
against `target`. A string such as `"user.name"` performs dotted nested access;
an integer path part indexes a sequence. A mapping spec evaluates each value
against the same target and preserves insertion order. A list spec evaluates
each element against the target and returns a list. A tuple `(subspec, func)`
first evaluates `subspec` and then passes the result to `func`. A callable spec
receives the current target. Missing access raises `PathAccessError` unless a
fallback spec such as `Coalesce` handles it.

`T` is the target specifier and supports path access and ordinary arithmetic or
comparison expressions. `S` accesses values stored in the evaluation scope.
`Val(value)` returns a literal without evaluating it. `Path(*parts)` expresses
literal path components, including keys containing dots; `Path.from_text(text)`
parses dotted text and `.values()` returns its components.

### Specification helpers

- `Spec(spec, scope=None)` wraps a reusable spec.
- `Coalesce(*subspecs, default=..., skip=..., skip_exc=...)` tries subspecs in
  order and returns the first non-skipped result or its default.
- `Call(func, args=None, kwargs=None)` evaluates argument specs before calling
  `func`. `Invoke(func)` evaluates a callable with `.specs(...)`,
  `.constants(...)`, or `.star(args=..., kwargs=...)` configuration.
- `Ref(name, subspec=...)` names and recursively reuses a spec; `Vars(...)`
  stores scope values; `Pipe(*steps)` chains specs/callables; `Fill(spec)`
  evaluates a structure while preserving literal holes; `Inspect` is available
  for inspection callbacks.

### Matching

`Match(spec)` validates a target and returns it when it conforms. Type specs,
mapping specs, `Regex`, `And`, `Or`, and `Not` compose matching rules.
`Optional(key)` marks a mapping key as optional, while `Required(key)` marks a
key or type as required. `Switch(cases, default=...)` selects the first case
whose path/spec is present and truthy. `Check(spec, type=..., validate=...,
default=...)` validates a value and can return its default when validation
fails. Match failures raise the appropriate `MatchError`/`TypeMatchError`.

### Mutation

`assign(obj, path, val, missing=None, repl=False)` and `delete(obj, path,
ignore_missing=False)` mutate a mapping/list/object in place and return the
same root object. `Assign` and `Delete` are spec forms for use inside
`glom(...)`. Missing intermediate mappings can be created with `missing=dict`.
Invalid paths and types raise the package’s normal mutation exceptions.

### Streaming and reductions

`Iter()` builds lazy iterable pipelines. Its `map`, `filter`, `chunked`,
`windowed`, `flatten`, `split`, `unique`, and `slice` methods return iterators;
terminal methods such as `all` and `first` materialize a result. `Sum`,
`Fold`, `Flatten`, and `Merge` reduce an iterable. `Group` and `Limit` from
`glom.grouping` provide deterministic encounter-order bucketing and bounded
groups.

### Errors, order, and determinism

Preserve input mapping order, iterable order, and stable first-occurrence
semantics. Do not promise object identity across processes, but in-place
mutation operations must return the original root within one process. Error
types and path details are observable and must not be silently swallowed.

## Implementation Notes

Implement the package in modular files (`core`, `matching`, `mutation`,
`reduction`, `streaming`, `grouping`, and the CLI) with a unified root export.
The scored contract intentionally excludes arbitrary callback serialization,
debug-output timing, Graphviz or external services, and unbounded filesystem
behavior. The verifier uses fixed named callbacks and a child-side adapter so
Python objects remain inside the candidate process. A minimal `setup.py` or
equivalent build backend is required; package installation must not download
the reference implementation or run upstream tests.
