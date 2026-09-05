# python-dotenv

## Project Description

Build an installable `python-dotenv` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution identity: `python-dotenv`; public import package begins at `dotenv`.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `Parsing with `dotenv_values`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `Reading one key`: preserve the documented object or module behavior, including state and side effects.
3. `Discovering a file`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `Loading the process environment`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- CPython 3.12.14 on the pinned Linux image.
- Distribution identity: `python-dotenv`; public import package begins at `dotenv`.
- Install from the workspace with `python -m pip install .`; do not download packages during evaluation.
- Declared build/runtime packages are supplied by the frozen evaluation image: `click==8.4.2`, `setuptools==80.10.2`, `wheel==0.45.1`
- Build metadata and package data must be present in the workspace and agree with the public import paths below.
- Agent, candidate, evaluator, Oracle, and control execution are network-isolated. Do not access GitHub, package registries, DNS, databases, or external services at runtime.
- Use deterministic local inputs. Do not rely on the current wall clock, host-specific absolute paths, undeclared environment variables, or an installed copy of the target package.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── a/
│   ├── __init__.py
│   └── (public modules documented in API Usage Guide)
```

The tree lists agent-owned public project files only. Add additional public modules when required by the API Usage Guide, but keep their import paths consistent with package metadata. Do not create evaluator-only files, hidden fixtures, or private reports in the generated project.

## API Usage Guide

The following is the task-specific public contract recovered from the local instruction and inventory. For every function, class, method, constant, export, and command named below, preserve its complete signature, accepted input domain, return type and shape, ordering, determinism, state/side effects, exceptions, and examples. When the source contract gives an optional argument or a compatibility alias, it is part of the required surface.

## Parsing with `dotenv_values`

```python
dotenv_values(
    dotenv_path=None,
    stream=None,
    verbose=False,
    interpolate=True,
    encoding="utf-8",
) -> dict[str, str | None]
```

Read from `dotenv_path`, or from a text `stream` when a path is not supplied.
Return an insertion-ordered dictionary. A missing input produces an empty
dictionary.

Each non-comment record is `KEY=VALUE`, optionally preceded by `export` and
surrounded by horizontal whitespace. A key without `=` maps to `None`; an
empty assignment maps to `""`. Blank lines and lines beginning with `#` are
ignored. An unquoted value drops trailing whitespace and a comment introduced
by whitespace followed by `#`; a `#` without preceding whitespace remains in
the value.

Single- and double-quoted values may contain spaces and newlines. Single
quotes decode `\\'` and `\\\\`. Double quotes decode backslash escapes for
backslash, quotes, alert, backspace, form-feed, newline, carriage return, tab,
and vertical tab. Unicode text is preserved. Invalid statements are skipped;
valid records before and after them remain available.

When `interpolate=True`, `${NAME}` uses a value already parsed in the same
file, otherwise the process environment, otherwise `""`. `${NAME:-default}`
uses `default` when the name is absent. Later duplicate assignments replace
earlier values and are used by later references. Bare `$NAME` is literal.
When `interpolate=False`, all references remain literal.

## Reading one key

```python
get_key(dotenv_path, key_to_get, encoding="utf-8") -> str | None
```

Return the parsed and interpolated value, or `None` when the key is absent,
has no assigned value, or the file is missing.

## Discovering a file

```python
find_dotenv(filename=".env", raise_error_if_not_found=False, usecwd=False) -> str
```

The supported deterministic mode is `usecwd=True`. Starting at the current
working directory, search that directory and each parent for a regular file
named `filename`. Return its absolute path. Return `""` when no file exists,
or raise `IOError` when `raise_error_if_not_found=True`.

## Loading the process environment

```python
load_dotenv(
    dotenv_path=None,
    stream=None,
    verbose=False,
    override=False,
    interpolate=True,
    encoding="utf-8",
) -> bool
```

Parse as described above and set every non-`None` value in `os.environ`.
Existing variables are retained by default and replaced when `override=True`.
Interpolation follows the same precedence: with `override=False`, an existing
environment value wins over a same-name value already parsed from the file;
with `override=True`, the parsed value wins. Return `True` when the parsed
mapping is non-empty and `False` for an empty or missing input. Keys without a
value do not modify the environment.

## Editing values

```python
set_key(
    dotenv_path,
    key_to_set,
    value_to_set,
    quote_mode="always",
    export=False,
    encoding="utf-8",
) -> tuple[bool | None, str, str]
```

Create the file when needed. Replace every assignment for the selected key in
place while preserving unrelated original text; otherwise append the record,
inserting a newline first when required. Return `(True, key, value)`.

`quote_mode` is `always`, `never`, or `auto`; another value raises
`ValueError`. `always` writes a single-quoted value. `never` writes it
unquoted. `auto` quotes values that are not entirely alphanumeric. A single
quote inside a quoted value is escaped as `\\'`. `export=True` prefixes the
record with `export `.

```python
unset_key(
    dotenv_path,
    key_to_unset,
    quote_mode="always",
    encoding="utf-8",
) -> tuple[bool | None, str]
```

Remove every record for the key while preserving all other text. Return
`(True, key)` when removed and `(None, key)` when the file or key is absent.
The `quote_mode` argument is accepted for compatibility and does not alter
removal behavior.

## Command string helper

```python
get_cli_string(path=None, action=None, key=None, value=None, quote=None) -> str
```

Build a space-separated command beginning with `dotenv`. Include `-q`, `-f`,
the action, key, and value when supplied, and surround a value containing a
space with double quotes.

## Module CLI

Run the CLI with `python -m dotenv`. Global options are `--file PATH`,
`--quote {always,never,auto}`, and `--export {true,false}`.

- `list [--format simple|json|shell|export]` emits keys in sorted order and
  omits keys with no value. JSON is indented and sorted. Shell and export
  formats shell-quote values; export format prefixes `export `.
- `get KEY` prints a non-empty value and exits 0. A missing or empty value
  produces no output and exits 1.
- `set KEY VALUE` applies the global quote/export policy, prints `KEY=VALUE`,
  and exits 0.
- `unset KEY` removes the key, prints `Successfully removed KEY`, and exits 0;
  an absent key exits 1 without stdout.
- `run [--override|--no-override] COMMAND...` replaces the command process
  with the `.env` values added. Override is enabled by default. Records with
  no value are omitted. A missing file or command exits nonzero.
- `--version` reports version `1.1.1`.


File mutation must use a temporary replacement or equivalent strategy so a
successful edit leaves a complete file. The verifier creates isolated
temporary directories and invokes candidate code only in an unprivileged
subprocess. Expected observations and grading output remain in the separate
verifier process.

```python
from io import StringIO
from dotenv import dotenv_values, load_dotenv, set_key, unset_key

assert dotenv_values(stream=StringIO("A=one\nB=${A}-two")) == {
    "A": "one",
    "B": "one-two",
}
assert load_dotenv(stream=StringIO("ENABLED=yes"), override=True) is True
assert set_key(".env", "GREETING", "hello world", quote_mode="auto") == (
    True,
    "GREETING",
    "hello world",
)
assert unset_key(".env", "GREETING") == (True, "GREETING")
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
dotenv_values(
    dotenv_path=None,
    stream=None,
    verbose=False,
    interpolate=True,
    encoding="utf-8",
) -> dict[str, str | None]
```

### Example 2: ordinary usage
```text
get_key(dotenv_path, key_to_get, encoding="utf-8") -> str | None
```

### Example 3: boundary or error behavior
```text
find_dotenv(filename=".env", raise_error_if_not_found=False, usecwd=False) -> str
```

### Example 4: boundary or error behavior
```text
load_dotenv(
    dotenv_path=None,
    stream=None,
    verbose=False,
    override=False,
    interpolate=True,
    encoding="utf-8",
) -> bool
```


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
