# Project Description

Build `ruff` version `0.16.4` as an installable Python command-line package.
The assessed surface is a deterministic subset of Ruff's linter and formatter
behavior. Your package must expose a `ruff` console command that works after a
non-editable offline installation from an otherwise empty workspace.

This task does not require Rust, native extensions, language-server support,
caching, notebook handling, plugin ecosystems, every Ruff rule, or byte-for-
byte diagnostic rendering. Implement the documented command behavior and keep
all code and packaging metadata in the submitted workspace.

## Natural Language Instruction

Create the installable `ruff` package from an empty `workspace/`. Implement the
documented `ruff` console command for deterministic local linting, formatting,
rule documentation, JSON diagnostics, stdin handling, safe single-import
fixes, and TOML configuration. Preserve exit statuses, filenames, locations,
configuration precedence, and the distinction between check, format, and rule
subcommands. The assessed subset does not require Rust or a complete linter.

# Supports

- Python 3.12 on Debian, installed as the distribution `ruff==0.16.4`.
- A `ruff` console-script entry point. A `python -m ruff` entry point may be
  provided as well, but it is not required by the assessed contract.
- Standard-library-only implementation code. `setuptools==80.9.0` is already
  available during image construction for normal Python package installation.
- No network access during agent or verifier execution. Do not download Ruff,
  rules, dependencies, or configuration at runtime.
- UTF-8 Python source files and TOML configuration files. The test inputs are
  small regular files in temporary directories.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── ruff/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── check.py
│   ├── format.py
│   └── rules.py
└── README.md
```

`pyproject.toml` must declare distribution version `0.16.4` and the `ruff`
console script. The module layout may be split differently when the console
entry point and documented package import remain available. Do not add a
network client, native compiler, language server, or generated rule database.

# API Usage Guide

## Package and command metadata

The installed distribution metadata name is `ruff`, its version is exactly
`0.16.4`, and it exposes exactly one console script named `ruff`. Running:

```text
ruff --version
```

exits with status `0` and writes `ruff 0.16.4` followed by a newline. Running
`ruff help check` exits successfully and documents the `check` command.

For command-oriented implementations, use these equivalent dispatch contracts:

```text
ruff_check(files: list[str], options: dict | None = None) -> exit status
ruff_format(files: list[str], mode: str | None = None) -> exit status
ruff_rule(code: str) -> exit status
```

These describe the three observable command families; the required public
entry point remains the `ruff` console script rather than a Python API.

## `ruff check`

```text
ruff check [OPTIONS] [FILES...]
```

`FILES` contains zero or more paths. `-` means standard input; when standard
input is used, `--stdin-filename NAME` supplies the displayed filename. A
missing path is a command-line error with exit status `2`. Otherwise, exit
status is `0` when there are no diagnostics and `1` when one or more
diagnostics are emitted.

The required lint rules are:

| Rule | Trigger | Required diagnostic behavior |
| --- | --- | --- |
| `F401` | an imported name is not otherwise used in the file | report the imported name on its import line; a line ending in `# noqa` or `# noqa: F401` suppresses it |
| `E501` | a physical source line is longer than the active line length | report the line; blank lines and the terminating newline do not contribute |

Default checking includes `F401` and has a line length of `88`. It is enough to
recognize ordinary `import name` and `from module import name` statements with
one imported name. A name that appears later as a Python identifier is used.

`--output-format json` writes one JSON array to standard output. Every item
has at least `code`, `message`, `filename`, and a `location` object with
one-based `row` and `column`. The exact human-readable default and concise
output is not prescribed, but it must include the rule code and filename.

`--fix` removes an unused single-name import diagnosed as `F401`, rewrites the
file, and returns `0` if no diagnostics remain. `--no-fix` disables that
rewrite even when `--fix` also appears. Standard input is never rewritten.

## Lint configuration

Without `--isolated`, a `pyproject.toml` in the working directory may contain:

```toml
[tool.ruff]
line-length = 20

[tool.ruff.lint]
select = ["F401", "E501"]
ignore = ["F401"]
```

`line-length` is a positive integer. `select` replaces the enabled required
rules, and `ignore` removes rules after selection. Rule lists contain the
literal codes `F401` and `E501`. `--isolated` ignores project configuration
and uses the defaults. `--config PATH` selects a TOML configuration file;
passing a nonexistent path is an exit-status-`2` error.

## `ruff format`

```text
ruff format [--check | --diff] [--isolated] [FILES...]
```

For the assessed Python snippets, formatting applies all of the following:

- normalize spaces around `=` in simple assignments;
- convert `def name(arg1, arg2,):` into a parenthesized one-argument-per-line
  definition with a trailing comma;
- convert a single-quoted string to double quotes when doing so does not
  require escaping a double quote;
- remove blank lines immediately inside a simple `if` block;
- ensure one final newline.

With a file path and no mode, `format` rewrites the file and exits `0`.
`--check` leaves files unchanged, reports each unformatted file, and exits `1`
when any rewrite would occur. `--diff` leaves files unchanged, writes a unified
diff containing both the original and formatted text, and also exits `1` when
changes are needed. For standard input, formatting writes the formatted text to
standard output and exits `0`; it never writes a file.

## `ruff rule`

```text
ruff rule F401
```

exits `0` and writes documentation identifying `F401` as the unused-import
rule. Unknown rule names are an exit-status-`2` error.

## Implementation Notes

- Design the project as a normal Python distribution with reproducible
  packaging metadata and a console entry point. The verifier installs it using
  `pip install --no-deps --no-build-isolation` into an isolated target.
- Paths in JSON diagnostics may be absolute or relative, but must identify the
  actual supplied path (or `--stdin-filename` for standard input).
- Rule selection, ignoring, `noqa`, fixing, formatting, and configuration are
  observable behavior. Do not hard-code the verifier's temporary file names.
- The evaluated inputs are deterministic and local. No behavior depends on
  wall-clock time, locale, a cache, a repository checkout, or network access.

## Examples

```text
ruff check --output-format json sample.py
```

```text
printf 'import os\n' | ruff check - --stdin-filename sample.py
```

```text
ruff format --check sample.py
ruff rule F401
```

## Error Handling and Boundary Conditions

- Missing paths, nonexistent `--config` files, unknown subcommands, unknown
  rules, and invalid option values return status `2` with a useful diagnostic.
- `ruff check` returns `0` for no diagnostics and `1` when diagnostics exist;
  JSON output remains a valid array and uses one-based row/column locations.
  `--no-fix` wins over `--fix`, and stdin is never rewritten.
- Formatting is deterministic for the same bytes and configuration. Empty
  files, files without a final newline, Unicode identifiers, and `# noqa`
  suppression follow the rules above. Agent, candidate, verifier, Oracle, and
  controls run with NoNetwork.
