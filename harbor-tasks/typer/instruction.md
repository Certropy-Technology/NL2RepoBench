# `typer` — build a type-hint driven CLI framework

## Project Description

Build the installable Python package `typer`: a library that turns ordinary
annotated Python functions into command line interfaces. A developer writes a
function with type hints and default values; your library derives the command's
arguments, options, conversions, help text and error messages from that
signature, then parses `argv` and calls the function with converted Python
objects.

The package must also ship a testing helper that runs an application in-process
and captures its streams and exit code, plus a small meta-CLI.

Users of this library are Python developers. The boundary is command
construction, argument parsing, value conversion, terminal output and process
exit codes. You are not building a shell, a daemon or a plugin system.

## Supports

- Python `3.12` on Linux, `x86_64`.
- Distribution name and import package: `typer`.
- `typer.__version__` must be exactly `"0.27.1"`.
- The project must be installable from its source tree with
  `pip install --no-deps --no-build-isolation .`, so declare a build backend
  that is already present in the environment (`pdm-backend`, `setuptools` and
  `wheel` are installed).
- Runtime dependencies available offline: `rich==15.0.0`,
  `shellingham==1.5.4`, `annotated-doc==0.0.4` (plus `markdown-it-py`, `mdurl`
  and `pygments` from the Rich chain). Do not add other third-party runtime
  dependencies and do not list standard-library modules as dependencies.
- Provide a `typer` console entry point mapped to `typer.cli:main`, and make
  `python -m typer` reach the same CLI.
- Ship `py.typed` markers for the package and for any vendored subpackage.
- No network access at build, install or run time.

## Licensing

Preserve the project's MIT license text. If you vendor or adapt another
project's parser or terminal code, its own notice must be retained alongside
the MIT license; do not relicense adapted bytes.

## API Usage Guide

### `typer.Typer`

```python
class Typer:
    def __init__(self, *, add_completion: bool = True, help: str | None = None) -> None: ...
    def command(self, name: str | None = None, *, help: str | None = None) -> Callable[[F], F]: ...
    def callback(self, *, help: str | None = None) -> Callable[[F], F]: ...
    def add_typer(self, typer_instance: "Typer", *, name: str | None = None, help: str | None = None) -> None: ...
    def __call__(self, *args, **kwargs): ...
```

- `command()` is a decorator that registers the decorated function as a
  command. It returns the function unchanged so it stays directly callable.
- With exactly one registered command and no `callback()`, the application is a
  single command: its parameters are parsed straight from `argv` with no
  subcommand name.
- With two or more commands, or with a `callback()`, the application is a group:
  the first non-option token selects a command.
- The command name defaults to the function name with underscores replaced by
  hyphens (`join_words` becomes `join-words`). An explicit `name=` overrides it.
- `callback()` registers a group-level function that runs before the selected
  command, receives its own parameters parsed from the tokens preceding the
  command name, and can be used to record shared state.
- `add_typer()` mounts another application as a subcommand group, so
  `app items show 21` reaches the `show` command of the mounted application.
- `add_completion=False` suppresses the shell-completion options.
- Calling the instance parses `sys.argv[1:]` and exits the process.

### Deriving parameters from a signature

For each parameter of a registered function:

- A parameter with no default is a required positional argument.
- A parameter with a default is an option named `--` plus the parameter name
  with underscores replaced by hyphens, and the default is used when the option
  is absent.
- A parameter annotated `bool` with default `False` is a flag: `--flag` sets it
  `True`, absence leaves it `False`. No value token is consumed.
- Values must be converted to the annotated type *before* the function is
  called, so the function body observes real Python objects.

Supported conversions include `str`, `int`, `float`, `bool`, `uuid.UUID`,
`datetime.datetime` (ISO 8601 such as `2020-01-02T03:04:05`),
`pathlib.Path` (a `PosixPath` on Linux), `enum.Enum` subclasses,
`Optional[T]`, `List[T]` and fixed-length `Tuple[...]`.

- An `Enum` parameter accepts the member *values* on the command line and the
  function receives the enum **member**, not the raw string.
- A `List[T]` option is repeatable: each occurrence appends one converted item,
  and the function receives a `list`. Its default may be an empty list.
- A fixed `Tuple[A, B]` option consumes exactly as many value tokens as the
  tuple has elements and converts each positionally, so
  `--pair x 7` with `Tuple[str, int]` yields `("x", 7)`.
- `Optional[T]` with default `None` leaves the value `None` when absent.

### `typer.Option` and `typer.Argument`

```python
def Option(default: Any, *param_decls: str, help: str | None = None,
           prompt: bool | str = False, envvar: str | None = None) -> Any: ...
def Argument(default: Any = ..., *, help: str | None = None) -> Any: ...
```

These return metadata objects used as parameter defaults; they are not the
runtime value. Both also work inside `typing.Annotated`.

- `...` (`Ellipsis`) as the default marks the parameter **required**.
- `*param_decls` gives explicit flag spellings, for example
  `typer.Option(..., "--token")`.
- `envvar="NAME"` reads the value from that environment variable when the
  option is absent on the command line. An explicit command-line value wins.
- `prompt=` requests the value interactively when it is missing. A string
  prompt is shown as `"<prompt>: "` on stdout, and the line the user types is
  echoed as part of that output.

### Output helpers

```python
def echo(message: Any = "", *, err: bool = False, nl: bool = True) -> None: ...
def secho(message: Any = "", *, err: bool = False, fg: str | None = None, ...) -> None: ...
def style(text: Any, *, fg: str | None = None, bold: bool = False, ...) -> str: ...
```

`echo` writes to stdout, or to stderr when `err=True`, appending a newline by
default. `style` returns a string with ANSI codes; when color is disabled the
styled text must still round-trip to its plain content. `typer.colors` exposes
named color constants such as `GREEN`.

Also expose `prompt`, `confirm`, `getchar`, `progressbar` and `launch`, and the
file/context types `Context`, `FileText`, `FileBinaryRead`.

### Exiting and errors

- `typer.Exit(code: int = 0)` is raised by user code to end the invocation with
  that exit code. Output written before it is kept.
- `typer.Abort()` aborts the invocation.
- A successful invocation exits `0`.
- A **usage error** (missing required option, unknown command, or a value that
  cannot be converted) exits `2`, writes nothing to stdout, and writes to
  **stderr** a short usage line, a hint line, and an error message. The usage
  and hint lines look like:

  ```text
  Usage: main [OPTIONS] ...
  Try 'main --help' for help.
  ```

  The error message text must state the cause using these forms:

  ```text
  Missing option '--token'.
  Invalid value for '--count': 'abc' is not a valid int.
  Invalid value for '--id': 'not-a-uuid' is not a valid UUID.
  Invalid value for '--level': 'mid' is not one of 'low', 'high'.
  No such command 'missing'.
  ```

  Rendering may decorate these messages (for example inside a Rich panel), so
  the exact surrounding frame is not fixed, but the message text above is.
- An exception raised by the user's function propagates out of the invocation
  rather than being converted into a usage error.

### `typer.testing.CliRunner`

```python
class CliRunner:
    def invoke(self, app, args=None, input=None, env=None, catch_exceptions=True,
               color=False, **extra) -> Result: ...
```

`invoke` accepts a live `Typer` object and runs it in the current process.

- `args` may be a list of tokens, or a string that is split with `shlex`.
- `input` supplies stdin text for prompts.
- `env` overlays environment values for the duration of the invocation only.
- stdin, stdout, stderr, environment, prompt input and ANSI handling are
  replaced during the call and restored afterwards. This isolation is
  single-threaded only.
- With `catch_exceptions=True` an escaping exception is captured instead of
  propagating.

`Result` exposes at least:

- `exit_code: int` — `0` on success, the code from `typer.Exit`, `2` for usage
  errors, and `1` when the user's function raised an uncaught exception;
- `stdout: str` and `stderr: str` — captured separately, with CRLF normalized;
- `output: str` — the mixed stream;
- `exception` — the captured exception instance, and `None` on success. A
  `typer.Exit` or a usage exit surfaces as a `SystemExit`;
- `exc_info` — the traceback tuple when an exception was captured;
- `return_value` — whatever the user's function returned.

### Shell completion and the meta-CLI

Provide Bash, Zsh, Fish and PowerShell completion script generation, detecting
the current shell through `shellingham`. Provide a `typer.cli` module with a
callable `main` that loads a `Typer` application from a Python file or module,
runs it, and can render Markdown documentation for its commands.

## Implementation Notes

- Parsing, conversion, help and error rendering must be deterministic for a
  fixed `argv`, environment and terminal width.
- Conversion failures are reported as usage errors on stderr with exit code
  `2`; they must not raise out of the invocation.
- Group state set by a `callback()` must be visible to the command that runs
  after it within the same invocation.
- Respect `NO_COLOR` and non-terminal streams by omitting ANSI sequences.
- Keep the package import-safe and side-effect free at import time.
- A small worked example:

  ```python
  import typer

  app = typer.Typer(add_completion=False)

  @app.command()
  def main(name: str, count: int = 1):
      typer.echo(f"{name} {count} {type(count).__name__}")

  # runner.invoke(app, ["ada", "--count", "3"]).stdout == "ada 3 int\n"
  ```
