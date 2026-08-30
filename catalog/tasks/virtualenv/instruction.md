# Build `virtualenv`

Create an installable Python package named `virtualenv` from an empty
workspace. This task targets the POSIX behavior of virtualenv 21.7.5 on
CPython 3.12. The package creates isolated Python environments locally; it
must never download Python, pip, wheels, or source code while it runs.

## Project Description

`virtualenv` is a command-line tool and Python package for creating a Python
environment rooted at a user-selected directory. An environment contains a
working Python executable, a `pyvenv.cfg` configuration file, a
`site-packages` directory, and optional shell activation scripts. The task is
limited to a deterministic Linux/POSIX subset and always creates environments
without seeding pip or other packages.

## Supports

- Provide Python package metadata for `pip install .`, a `virtualenv` package,
  and a `python -m virtualenv` module entry point.
- Support CPython 3.12 and declare the runtime dependencies required by your
  implementation. The evaluation image already contains the task's declared
  dependency closure, so do not install dependencies or use the network at
  runtime.
- Support `--help` and `--version`; `--version` must identify version
  `21.7.5`.
- Create environments with `DEST --no-seed`. The destination must contain a
  functional `bin/python`, `pyvenv.cfg`, and a Python `site-packages`
  directory. Executing `bin/python -c 'import sys; ...'` must report a prefix
  different from `base_prefix`.
- Reject a destination that is an existing regular file or contains the POSIX
  path-list separator (`:`), returning a non-zero CLI status.
- Do not seed pip, setuptools, wheel, or any downloaded artifact. Creation
  must work with network access unavailable.

## API Usage Guide

### Module entry point

Run the package as:

```bash
python -m virtualenv [OPTIONS] DEST
```

`DEST` is a path to the new environment. A successful invocation returns zero.
It may write informational text, but must not require an interactive terminal.
All options below are accepted before or after `DEST` unless an option has its
own argument.

`--no-seed` disables package seeding. It is required by the creation contract
in this task. `--without-pip` is accepted as an equivalent no-seed request.
`--activators LIST` accepts a comma-separated list of activation script types;
an empty string creates no activation scripts, and `bash` creates
`bin/activate` containing `VIRTUAL_ENV` handling. With no explicit
`--activators`, bash activation is included.

`--no-vcs-ignore` prevents creation of `.gitignore`. Otherwise a newly created
environment contains `.gitignore` with the two lines
`# created by virtualenv automatically` and `*`. Existing `.gitignore` files
are not replaced.

`--prompt VALUE` writes a `prompt` field in `pyvenv.cfg`; quote the value when
needed so it can be read back as one string. A value of `.` means the basename
of the parent directory of the destination.

`--clear` recreates an existing environment directory and removes files that
were in that directory. `--system-site-packages` writes
`include-system-site-packages = true`; the default writes `false`.
`--copies` and `--symlinks` request the corresponding Python executable
strategy. On this Linux target both forms must create a usable environment;
the `--symlinks` executable is a symbolic link. `-p PATH` and `--python PATH`
select the base interpreter and must reject a missing path. `--creator venv`
is accepted and creates the same task-visible environment shape.

`--app-data PATH` selects a local cache directory. `--reset-app-data` clears
that directory before use. `--discovery builtin` is accepted. An unavailable
discovery name such as `pyenv` must fail with a non-zero status and a message
mentioning the requested name.

### `virtualenv.run`

Import path: `from virtualenv.run import cli_run, session_via_cli`.

`cli_run(args: list[str], options: object | None = None,
setup_logging: bool = True, env: MutableMapping[str, str] | None = None)`
creates the requested environment and returns a session object. The returned
object exposes a `creator` with at least `dest`, `exe`, `bin_dir`, and
`pyenv_cfg` path-like attributes. It raises `SystemExit` for `--help`,
`--version`, and invalid CLI requests. `session_via_cli` has the same arguments
and returns the parsed session without creating the destination.

### `virtualenv.create.pyenv_cfg.PyEnvCfg`

Import path: `from virtualenv.create.pyenv_cfg import PyEnvCfg`.

`PyEnvCfg.from_file(path: pathlib.Path) -> PyEnvCfg` reads `key = value` lines
from an existing configuration file. `from_folder(folder)` reads
`folder / 'pyvenv.cfg'`. Instances support `cfg[key]`, `key in cfg`,
`cfg[key] = value`, `cfg.update(mapping)`, `cfg.refresh()`, and `cfg.write()`.
`write()` preserves insertion order, writes UTF-8 `key = value` lines, and
quotes a non-empty `prompt` value. Values surrounded by matching single or
double quotes are unquoted when read.

## Implementation Notes

Use only local filesystem operations and subprocesses. The verifier runs each
candidate call as an unprivileged user and provides no network. Do not depend
on a global `virtualenv` installation, current-directory source imports, or
external cache contents. Paths in `pyvenv.cfg` can vary by host; preserve the
documented keys and relationships rather than hard-coding host paths.
