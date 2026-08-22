# Build `doit`

Create a complete, installable Python project named `doit` from an empty
workspace. The project is a task automation library and command-line runner.
It discovers Python task definitions, resolves dependencies, skips work that is
up to date, executes shell or Python actions, persists task state, and exposes
extension points for commands, loaders, reporters, storage backends, and file
change checkers.

## Project Description

`doit` uses ordinary Python modules as task files. A function whose name starts
with `task_` returns a task dictionary or yields dictionaries for related
subtasks. Tasks may run command strings, argument-vector commands, or Python
callables. They may declare input files, output targets, task dependencies,
custom up-to-date checks, setup and teardown work, parameters, cleanup actions,
and values consumed by later tasks.

The distribution and import package are both named `doit`. The project version
is `0.38.0.dev0`; `doit.__version__` and `doit.version.VERSION` expose the tuple
`(0, 38, "dev0")`.

## Supports

- Support Python 3.10 and newer Python 3 versions.
- Provide an installable top-level `doit/` package and a `pyproject.toml` using
  a standard Python build backend. Both editable and regular installation must
  work.
- Install a `doit` console script that calls `doit.__main__:main`. The same CLI
  must work as `python -m doit`.
- Declare no mandatory third-party runtime dependencies. On Python 3.10,
  reading TOML configuration requires an optional TOML parser such as `tomli`.
  `cloudpickle` is optional and broadens multiprocessing support for dynamically
  created callables. IPython and Linux `strace` integrations are optional.
- Normal task loading and execution do not require network access. User-defined
  actions are intentionally allowed to access the filesystem and launch local
  processes, so those effects must follow the caller's environment and process
  permissions.
- Use UTF-8 for TOML configuration and for text output files created by CLI
  options. Preserve ordinary platform path, shell, process, and DBM behavior
  rather than pretending every operating system has identical facilities.
- Keep the installed project usable without its source tests or documentation.

## API Usage Guide

### Root package

The root package exports these five names through `doit.__all__`:

```python
def get_var(name, default=None): ...
def run(task_creators): ...
def create_after(executed=None, target_regex=None, creates=None): ...
def task_params(param_def=None): ...
class Globals: ...
```

It also provides:

```python
def get_initial_workdir(): ...
def load_ipython_extension(ip=None): ...
```

`get_var` reads a `name=value` variable parsed from the current CLI invocation.
Before CLI parsing has initialized variable state it returns `None`; afterward,
an absent name returns `default`. A command-line token beginning with `-` is an
option, not a variable.

`run(task_creators)` runs tasks from a module or namespace dictionary instead
of loading `dodo.py`. It uses the process arguments after the script name and
terminates with the resulting CLI status via `SystemExit`.

`get_initial_workdir()` returns the directory from which task-file discovery
started. Loading a dodo file may change the process working directory to the
task file's directory or to the explicit `--dir` directory.

`Globals.dep_manager` exposes the active dependency manager while a task command
is running. It is `None` outside that lifecycle. Code that uses it must not
assume a permanent global database connection.

### Task discovery and creation

The default task file is `dodo.py`. Task creators are ordinary functions or
bound methods named `task_<base-name>`. An object with a callable
`create_doit_tasks` attribute is also a task creator. Creators are evaluated in
source-definition order. A creator may return one task dictionary, a `Task`
instance, a generator of task dictionaries, or nested generators. Returning
`None` creates no task; an empty generator creates an empty group task.

A single returned dictionary uses the creator suffix as its task name unless it
contains `basename`. A yielded dictionary with `name` uses that value as the
subtask suffix and forms names such as `build:debug`; the base task represents
the group. A yielded dictionary may instead use `basename` without `name` to
create a standalone task. Duplicate full task names, a single returned
dictionary containing `name`, a yielded dictionary containing neither `name`
nor `basename`, or a task name colliding with a command is invalid.

The task dictionary supports these fields:

| Field | Contract |
| --- | --- |
| `actions` | Required list/tuple of actions, or `None` for a group/delayed placeholder. |
| `basename`, `name` | Base-name override and yielded subtask suffix as described above. |
| `file_dep` | Input path strings or `pathlib` paths. |
| `targets` | Output path strings or `pathlib` paths; duplicate target ownership is invalid. |
| `task_dep` | Task names or wildcard names that must complete first. |
| `uptodate` | Booleans, `None`, shell-command strings, callables, or `(callable, args, kwargs)` tuples. |
| `calc_dep` | Tasks whose action results may add dependency metadata before dispatch continues. |
| `setup` | Tasks run only when this task has been selected to execute. |
| `clean` | `True` to remove targets, or a sequence of cleanup actions. |
| `teardown` | Actions run after execution, in reverse task teardown order. |
| `doc` | Task description; otherwise the first nonblank creator-docstring line is used. |
| `params` | Task action option declarations. |
| `pos_arg` | Action argument that receives remaining positional CLI values. |
| `verbosity` | `0`, `1`, `2`, or `None`. |
| `io` | I/O options; `{"capture": False}` disables action output capture. |
| `getargs` | Mapping from an action argument to `(task_name, value_name)`; `value_name=None` passes the full value dictionary. |
| `title` | Callable receiving the `Task` and returning its display title. |
| `watch` | Paths exposed for watch integrations. |
| `meta` | Arbitrary metadata not interpreted by the core runner. |

Unknown fields, invalid field types, and a task name containing `=` raise
`doit.exceptions.InvalidTask`.

`task_params(param_def)` decorates a creator with command-line parameter
declarations. It requires a list. Creator parameters are parsed before the task
dictionary exists, so a creator using this decorator cannot also use the task's
`params` field.

`create_after(executed=None, target_regex=None, creates=None)` delays a creator
until the named task has executed. `target_regex` describes targets that the
delayed creator may produce. `creates` supplies exact task base names when they
cannot be known without running the creator.

### Task parameters

Each parameter declaration is a dictionary with required `name` and `default`
entries. Optional entries are:

- `short` and `long` for CLI spellings;
- `type`, a conversion callable (`str` by default, with `bool` treated as a
  flag and `list` accepting repeated values);
- `choices`, a sequence of `(value, description)` pairs;
- `help`; and
- `inverse`, the long spelling of the opposite boolean flag.

Invalid conversions or choices raise a command parse error. Parsed options are
provided to Python actions by matching parameter name and to command actions by
string expansion. If `pos_arg` is set, all unparsed positional values after the
task options are assigned to that argument; another task name cannot follow it
unambiguously.

### Actions

The action module exposes these principal interfaces:

```python
class BaseAction: ...

class CmdAction(
    action, task=None, save_out=None, shell=True,
    encoding="utf-8", decode_error="replace", buffering=0, **popen_kwargs
): ...

class PythonAction(py_callable, args=None, kwargs=None, task=None): ...

def create_action(action, task_ref, param_name): ...
```

Action conversion follows these rules:

- A string becomes `CmdAction(..., shell=True)`.
- A list becomes `CmdAction(..., shell=False)` and may contain strings and
  `pathlib` path values, which are converted to strings.
- A callable becomes `PythonAction`.
- A tuple has one to three elements `(callable, args, kwargs)` and becomes
  `PythonAction`.
- An existing `BaseAction` instance is retained and attached to the task.

`CmdAction` accepts the normal `subprocess.Popen` keyword arguments except
`stdout` and `stderr`, which are controlled by the runner. For string commands,
old-style placeholders can receive `targets`, `dependencies`, `changed`, task
options, positional arguments, and `getargs` values. The configured action
format may use old, new, or both string formatting styles. Argument-vector
actions are not string-expanded.

Captured stdout and stderr are available as `action.out` and `action.err`.
When `save_out` is set, captured stdout is stored in the action values under
that name. Process status `0` succeeds; a nonzero status up to `125` produces
`TaskFailed`, while a status greater than `125` produces `TaskError`.
Decoding follows `encoding` and `decode_error`: invalid bytes are replaced by
default, while strict decoding propagates the decoding failure from the stream
reader and terminates the affected child instead of reporting success.

`PythonAction` rejects classes, built-in functions, non-callables, non-list or
non-tuple positional argument containers, and non-dictionary keyword argument
containers. The callable result means:

- `True` or `None`: success without a saved result;
- `str`: success and that string is the action result;
- `dict`: success and the dictionary is both result and saved values;
- `False`: `TaskFailed`;
- `TaskFailed` or `TaskError`: return that failure; and
- any other value or raised exception: `TaskError`.

When a Python action signature asks for `task`, `targets`, `dependencies`, or
`changed`, the runner supplies the corresponding task metadata unless the
argument was already bound positionally. These reserved metadata parameters
must not define default values. Parsed task options and positional values are
also supplied by name; a `**kwargs` action receives unmatched options.

Task actions run sequentially. Execution stops on the first failed action. A
task's final action result is persisted, and dictionaries returned by actions
are merged into task values. Output verbosity is `0` for captured stdout and
stderr, `1` for captured stdout with live stderr, and `2` for live stdout and
stderr. The global CLI setting wins when it is forced.

### Dependencies and persisted state

A task is not up to date when any applicable condition holds:

- it has no file dependency and no effective true up-to-date condition;
- an `uptodate` item evaluates false;
- a target is missing;
- a file dependency is missing, added, removed, or changed; or
- the configured file checker differs from the one used for saved state.

`None` up-to-date results are ignored. Callable checks may receive the current
`task` and its previously saved `values`. A string check runs through the shell
and is true only when its command exits zero. A true check does not override a
missing target or changed input.

The default `MD5Checker` persists modification time, size, and content MD5. An
unchanged modification time short-circuits content hashing; a changed size is a
change; otherwise content MD5 decides. `TimestampChecker` compares only mtime.
The public checker protocol is:

```python
class FileChangedChecker:
    def exists(self, file_path): ...
    def info(self, file_path): ...
    def check_modified(self, file_path, file_stat, state): ...
    def get_state(self, dep, current_state): ...
```

Task dependencies constrain execution order but do not by themselves make a
task up to date. A matching target/file-dependency path creates an implicit task
dependency. Wildcards select matching tasks. Setup tasks run only after the
dependent task is known to need execution. Teardown actions are attempted in
reverse registration order even when later work fails.

`getargs` creates the required setup dependency and passes one named saved value
or the whole value dictionary. For a group task, it produces a mapping keyed by
subtask suffix. `doit.task.result_dep(task_name, setup_dep=False)` compares the
persisted result of another task and also establishes the appropriate ordering
dependency.

State backends implement `set`, `get`, `in_`, `remove`, `remove_all`, and
`dump`. Built-in backend names are `dbm`, `json`, and `sqlite3`. The default is
platform DBM and the default state path is `.doit.db`. JSON and SQLite preserve
the same logical per-task dictionary, including file signatures, values,
results, ignore markers, checker identity, and the dependency list. Corrupt or
unsupported storage raises a database/command error instead of silently
claiming that tasks are current.

### Runner behavior

`Runner` executes ready tasks serially. `MRunner` uses multiprocessing and
`MThreadRunner` uses threads. The CLI selects serial execution when
`--process=0`; a positive process count uses the requested parallel type.
Actions within one task always remain sequential, and a task is dispatched only
after required dependencies are ready.

The run status codes are:

```text
0  all selected tasks succeeded
1  at least one task failed
2  an execution, dependency, or setup error occurred
3  command parsing, task loading, or another pre-run/internal CLI error occurred
```

Without `--continue`, execution stops after the first failure/error. With it,
independent tasks may continue, but tasks whose dependencies failed do not run.
`--always-execute` bypasses an up-to-date decision, but an explicitly ignored
task remains ignored. `--single` runs only selected tasks/subtasks without their
normal task dependencies.

Multiprocessing requires task data and dynamic creators to be serializable.
The standard library `pickle` is the fallback; installed `cloudpickle` is used
when available. If a task cannot be serialized, raise `InvalidTask` with an
actionable message. Thread mode does not impose the same pickling restriction.
Parallel completion and live output order are not a deterministic API promise.

### Command-line interface

The general form is:

```text
doit [run] [GLOBAL_OPTIONS] [TASK_OR_TARGET TASK_OPTIONS ...] [NAME=VALUE ...]
```

`run` is the default command. Global task-file options include `-f/--file`,
`-d/--dir`, and `-k/--seek-file`. Common state options include `--db-file`,
`--backend`, and `--check_file_uptodate`. `--version` prints the tuple as a
dotted version followed by the installed library path. `--help` and
`doit help` print command usage.

The built-in command names and required behavior are:

- `run`: select tasks or targets, resolve dependencies, and execute them. Key
  options include `-a/--always-execute`, `-c/--continue`, `-s/--single`,
  `-n/--process`, `-P/--parallel-type`, `-r/--reporter`, `-o/--output-file`,
  `-v/--verbosity`, `--failure-verbosity`, and `--auto-delayed-regex`.
- `list`: list public base tasks alphabetically by default. `--sort=definition`
  preserves definition order; `--all` includes subtasks; `--private` includes
  names beginning with `_`; `--quiet`, `--status`, `--deps`, and `--template`
  control columns and rendering.
- `info TASK`: print declared metadata and, unless `--no-status` is used, the
  current status and reasons. It accepts exactly one task.
- `clean`: run cleanup actions or remove targets. `--dry-run` avoids actions
  unless a Python cleanup explicitly accepts the `dryrun` argument. `--clean-dep`
  follows task dependencies, `--clean-all` selects all tasks, and `--forget`
  also removes saved state. Target removal uses reverse lexical order and does
  not remove nonempty directories.
- `forget`: remove successful-run state for selected/default tasks. `--all`
  removes all state and `--follow-sub` follows dependencies/subtasks.
- `ignore`: persist ignore markers for selected tasks and their subtasks. It
  refuses an empty selection.
- `reset-dep`: recompute dependency signatures without executing actions. It
  reports missing dependencies and preserves existing saved values/results.
- `dumpdb`: print an iterable DBM dependency database and reject DBM variants
  that cannot be iterated safely.
- `tabcompletion`: emit bash or zsh completion source, with an option to embed
  the current task names or discover them dynamically.
- `strace`: on supported Linux systems, wrap one command-action task and report
  files opened for reading/writing. It is diagnostic, requires `strace`, and is
  not a portable dependency detector.
- `help`: show command help, task dictionary help, or task parameter help.

Built-in reporters are `console`, `executed-only`, `json`, `zero`, and
`error-only`. Console output distinguishes execution, up-to-date skips, ignored
tasks, failures, and errors. JSON reporting emits one final JSON document with
per-task status, captured output/error, and timing fields. Exact timestamps and
parallel event order must not be treated as stable text.

### Configuration

Configuration sources are merged from API `extra_config`, `pyproject.toml`,
`doit.cfg`, and `DOIT_CONFIG` from the task module. Later applicable values
override earlier defaults according to command parsing. `pyproject.toml` uses:

```toml
[tool.doit]
[tool.doit.commands.<command>]
[tool.doit.tasks.<task>]
[tool.doit.plugins.command]
[tool.doit.plugins.loader]
[tool.doit.plugins.backend]
[tool.doit.plugins.reporter]
```

Legacy INI uses `GLOBAL`, one section per command, `task:<name>`, and uppercase
plugin category sections. INI option case is preserved. TOML loading tries
`tomllib`, then `tomli`, then `tomlkit`; when no parser is available it warns
instead of failing unrelated commands.

### Plugins and extension APIs

Plugins may be configured as `"module:attribute"` references or exposed as
installed entry points. Entry-point groups are `doit.COMMAND`, `doit.LOADER`,
`doit.BACKEND`, and `doit.REPORTER`. Installed entry points override a local
configuration entry with the same name. Plugin import is lazy and cached.

```python
class PluginEntry:
    def __init__(self, category, name, location): ...
    def get(self): ...
    def load(self): ...

class PluginDict(dict):
    def add_plugins(self, cfg_data, category): ...
    def get_plugin(self, key): ...
    def to_dict(self): ...
```

`PluginEntry.load()` splits `module:attribute`, imports the module, and returns
the attribute. Missing modules and missing attributes raise errors that identify
the plugin category and location. `PluginDict.get_plugin()` returns ordinary
values unchanged and resolves `PluginEntry` values.

The documented framework interfaces also include:

```python
class Command:
    @classmethod
    def get_name(cls): ...
    def parse_execute(self, in_args): ...
    def execute(self, opt_values, pos_args): ...
    def help(self): ...

class TaskLoader2:
    def setup(self, opt_values): ...
    def load_doit_config(self): ...
    def load_tasks(self, cmd, pos_args): ...

class ModuleTaskLoader(TaskLoader2): ...
class DoitMain:
    def __init__(self, task_loader=None,
                 config_filenames=("pyproject.toml", "doit.cfg"),
                 extra_config=None): ...
    def run(self, all_args): ...
```

Custom reporters receive lifecycle calls such as `initialize`, `get_status`,
`execute_task`, `add_success`, `add_failure`, `skip_uptodate`, `skip_ignore`,
`cleanup_error`, `runtime_error`, `teardown_task`, and `complete_run`. A custom
backend follows the state backend protocol above. A custom loader should use
`TaskLoader2`; the old `TaskLoader` constructor raises `NotImplementedError`.

### Utility APIs

`doit.tools` provides:

```python
def create_folder(dir_path): ...
def title_with_actions(task): ...
def run_once(task, values): ...
class config_changed(config, encoder=None): ...
class timeout(timeout_limit): ...
class check_timestamp_unchanged(file_name, time="mtime", cmp_op=operator.eq): ...
class LongRunning(CmdAction): ...
class Interactive(CmdAction): ...
class PythonInteractiveAction(PythonAction): ...
def set_trace(): ...
```

`create_folder` creates parent directories idempotently. `run_once` records a
value after the first successful execution. `config_changed` accepts a string
or dictionary; dictionaries are JSON encoded with sorted keys and an optional
encoder before digest comparison. `timeout` accepts integer seconds or
`datetime.timedelta` and compares wall-clock time with the last success.
`check_timestamp_unchanged` supports `atime/access`, `ctime/status`, and
`mtime/modify`, stores the selected timestamp, and delegates equality to
`cmp_op`. A missing path raises the underlying OS error.

`LongRunning` streams a shell process until it exits, ignores the process exit
status, and treats `KeyboardInterrupt` as the normal stop path. `Interactive`
streams I/O and fails on a nonzero process result. `PythonInteractiveAction`
executes a Python callable without redirected I/O; exceptions become
`TaskError`, string and dictionary returns are recorded, and other return values
do not create an explicit failure.

The public exception hierarchy includes `InvalidCommand`, `InvalidDodoFile`,
`InvalidTask`, `TaskFailed`, `TaskError`, `UnmetDependency`, `SetupError`, and
`DependencyError`. User input and task-definition problems use the `Invalid*`
exceptions; action failures/errors use the `BaseFail` result hierarchy so the
runner can classify status without confusing a model failure with an internal
crash.

## Implementation Notes

- Preserve deterministic order where promised: creator definition order,
  generator yield order, action order, explicit dependency constraints, default
  alphabetical listing, definition-order listing, and reverse teardown/target
  cleanup order. Do not promise a fixed order for sets, file-dependency
  internals, installed entry points, DBM iteration, or parallel completion.
- Treat filesystem timestamps as environment observations. Tests should set
  mtimes explicitly or inject/mask clock reads; sleeps are not a reliable
  correctness mechanism. `timeout` and JSON reporter timestamps likewise need
  normalization in deterministic callers.
- Preserve shell and argument-vector distinctions. Do not emulate shell quoting
  by joining a list into a string. Bound every spawned process and propagate
  its status while cleaning up descendants on cancellation.
- Entry-point discovery must see only the installed environment supplied by the
  caller. Do not bake host plugins into the package or depend on their order.
- Keep persisted state scoped to the requested backend/path. A clean temporary
  workspace must not inherit another run's `.doit.db`, plugin metadata, task
  module cache, current directory, environment variables, or global CLI values.
- Keep candidate implementation and verification separate. The installed
  package must work when verifier tests are absent, and no test result or reward
  file is part of this public API.

Example task file:

```python
from pathlib import Path

from doit import get_var
from doit.tools import run_once


def write_message(targets, message):
    Path(targets[0]).write_text(message + "\n", encoding="utf-8")
    return {"message": message}


def task_message():
    output = "message.txt"
    return {
        "actions": [(write_message, (), {"message": get_var("message", "hello")})],
        "targets": [output],
        "uptodate": [run_once],
        "clean": True,
        "verbosity": 2,
    }
```

The first successful run creates the target and saves the value. A later run is
up to date while the target and persisted state remain valid; deleting the
target selects the task again. `doit clean message` removes the target without
requiring verifier files in the project.
