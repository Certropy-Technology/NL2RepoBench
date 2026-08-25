# Project Description

Create an installable Python package named `python-dotenv`, imported as
`dotenv`. It reads shell-like key/value records from `.env` files, optionally
interpolates `${NAME}` references, discovers files in parent directories,
loads values into `os.environ`, edits files without discarding unrelated
content, and provides the `python -m dotenv` command line interface.

The supported surface is intentionally bounded to the APIs and CLI commands
below. IPython integration, debugger/frame-based discovery, internal parser
objects, logging text, and Windows-specific process behavior are outside this
task.

# Supports

- CPython 3.12 on Linux.
- Distribution name `python-dotenv`, version `1.1.1`.
- Import package `dotenv` and module entry point `python -m dotenv`.
- A setuptools build. Runtime CLI support uses `click>=5.0`.
- UTF-8 by default, with explicit alternate encodings where documented.
- No network access or external services at runtime.

# API Usage Guide

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

# Implementation Notes

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
