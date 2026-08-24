# `doit` Static Authoring Audit

Status: **blocked**. This task-local directory contains a public declarative
source, a public behavior specification, and static provenance/collection
evidence only. It contains no copied upstream source or license bytes, upstream
test bytes, hidden assertions, private command plan, dependency wheelhouse,
Docker file, Harbor bundle, verifier code, Oracle solution, result artifact,
secret, or shared catalog/dataset change.

## Decision

Keep `doit` blocked. The exact source is a strong task-automation candidate and
its CLI offers a natural subprocess seam, but the current evidence does not
satisfy a production authoring gate:

- no Python/OS/base-image, shell, locale, filesystem, DBM, or process policy is
  frozen;
- build, test, optional, and system dependencies are not a hash-locked offline
  artifact;
- effective test behavior changes with `strace`, `cloudpickle`, Python, DBM,
  locale, and multiprocessing availability;
- the upstream suite directly imports and patches rich candidate objects and
  cannot be passed through the generic stateless JSON call client; and
- no private tests, allowlisted command plan, task-specific scenario adapter,
  frozen denominator, Oracle runs, or controls exist in this lane.

The discovery report's `severity medium` describes authoring risk, not benchmark
difficulty. This blocked record therefore leaves production difficulty unknown
instead of silently reinterpreting that label.

## Candidate Identity

The candidate was recovered from the Python CLI/data/serialization discovery
report stored in the local subagent record. That report identified:

- project: `pydoit/doit`;
- category: CLI/task automation;
- priority: A;
- requested revision:
  `1f9cbbce78a93f96a35abf2db5425361e2abf142`;
- license: MIT in `LICENSE` and `pyproject.toml`;
- discovery estimate: approximately 4,500-6,000 production LOC and 27 test
  modules; and
- risks: filesystem timestamps, subprocess behavior, plugin loading, and
  platform-specific command behavior.

A detached checkout at `/tmp/nl2repo-doit-audit` resolved exactly to the full
requested SHA. The immutable commit evidence is:

```text
commit:         1f9cbbce78a93f96a35abf2db5425361e2abf142
tree:           525dc089b45025e8db6325967693bcebd82fd7ce
author date:    2026-02-12T20:52:51+08:00
committer date: 2026-02-12T20:52:51+08:00
subject:        pyproject. fix rut version.
describe:       0.37.0-10-g1f9cbbc
submodules:     none
```

At audit time the commit was reachable from upstream `master`; the catalog
pins the full commit and never relies on that mutable branch. The detached
checkout remained clean after all inspection and collect-only commands.

No existing legacy task, catalog task, or case-insensitive `pydoit`/`doit`
duplicate was found outside this task directory. Final dataset integration must
still perform its own semantic duplicate review, especially against other CLI
and automation tools.

## Source Archive and License

The source lock in `task.toml` is the unprefixed archive produced directly from
the detached commit:

```text
command:         git archive --format=tar HEAD
archive bytes:   1,617,920
archive members: 232 (including directory entries)
tracked files:   218
sha256:          d9765a508bc4ba6a61c586883de7fa9cc38abc7acdc8caf32c98d64834c2cfcd
```

Two independent archive commands produced byte-identical output. The archive
contains all 29 runtime Python modules and all 34 tracked test/support Python
files. It is not a GitHub-generated repack, and no archive bytes are stored in
this catalog.

License evidence is internally consistent:

- `LICENSE` is 1,095 bytes, 23 newline-terminated lines;
- Git blob: `b680a3da2aa7c4a2d3f19209a964022f81922936`;
- file SHA-256:
  `d4af33f3d435ab72c9c28abb14ed4a64bb3036c6ebcd54576f4619ff9d50c439`;
- the text is the standard MIT permission, warranty, and liability language
  with `Copyright (c) 2008-present Eduardo Naufel Schettino`;
- `pyproject.toml` declares `license = {text = "MIT"}` and the MIT classifier;
  and
- the discovery report independently identified GitHub's commit-pinned license
  file as MIT.

`pyproject.toml` itself is 2,180 bytes, Git blob
`96b140c4ea294528a8406b5787edfebe4d5b33c6`, and SHA-256
`7c750b08506aae2f9604355ec3450860bec7f0ad96e7d298093efb9c6e1d61ac`.
No transitive build/test dependency license review is claimed.

## Package Boundary and LOC

The candidate implementation boundary is the tracked `pyproject.toml` and the
29 Python modules directly under `doit/`. The build metadata installs exactly
the `doit` package and the `doit = "doit.__main__:main"` console script. The
package contains no C, Cython, Rust, generated extension, bundled wheel, or
vendored third-party runtime tree.

Physical line counts were computed from the exact checkout with
`str.splitlines()`. A noncomment line is nonblank and does not begin with `#`
after leading whitespace; docstrings remain code/documentation lines. The
method is recorded so the count is reproducible and is not confused with
tokenized logical SLOC.

| Tree | Python files | Physical | Nonblank | Nonblank/non-`#` |
| --- | ---: | ---: | ---: | ---: |
| `doit/*.py` | 29 | 7,541 | 6,175 | **5,587** |
| `tests/*.py` including support | 34 | 8,481 | 7,124 | 6,714 |

The 5,587 implementation count reproduces the discovery range. The largest
runtime modules are `dependency.py` (748 physical lines), `task.py` (677),
`control.py` (654), `cmd_base.py` (619), `runner.py` (577), and `action.py`
(556). This is a multi-module task runner, not a single CLI wrapper.

The candidate repository also tracks documentation, samples, completion files,
and project development tasks. Those explain public behavior but are not part
of the candidate import boundary. A future candidate repository still needs
ordinary packaging/readme/license files; verifier tests must not be copied into
the candidate workspace.

## Public API Inventory

The root `doit.__all__` is the authoritative narrow export list:

```text
get_var, run, create_after, task_params, Globals
```

The root module additionally exposes `__version__`, `get_initial_workdir`, and
the imported IPython extension hook. Public documentation also treats task
dictionaries, action classes, tools, loader/command/reporter interfaces,
storage/checker protocols, plugin categories, and the CLI commands as supported
extension surfaces.

Because most modules do not define `__all__`, a single "public API count" would
otherwise be ambiguous. An exact AST heuristic over module-level names not
beginning with `_` found:

```text
module-level functions:             35
module-level classes:               82
module-level public definitions:   117
public methods on those classes:   183
of which @property methods:          6
combined definition/method heuristic: 300
```

This 300 value is an inventory cross-check, not a promise that every unprefixed
implementation class is stable. The public specification deliberately groups
the supported behavior into these reviewable surfaces:

1. root helpers and version metadata;
2. task discovery, task dictionaries, subtasks, delayed creation, and task
   parameters;
3. command and Python actions, output capture, return classification, and magic
   action arguments;
4. file/task/setup/calc/result dependencies, persistent values, and cleanup;
5. serial, multiprocessing, and threaded runners;
6. the built-in CLI commands and reporters;
7. TOML/INI/dodo configuration and command-line variables;
8. command/loader/reporter/backend/plugin extension protocols;
9. file checkers and DBM/JSON/SQLite backends; and
10. public tools and exception classes.

Future test-to-spec traceability must name which of the 117/300 heuristic
symbols are intentionally tested. Private helpers, mocks, and implementation
seams must not become accidental public requirements merely because the source
suite imports them.

## Packaging and Dependency Closure

The exact `pyproject.toml` declares:

```text
distribution:       doit
version:            0.38.0.dev0
requires-python:    >=3.10
build backend:      setuptools.build_meta
build requirement:  setuptools>=68.0
runtime depends:    []
console script:     doit = doit.__main__:main
```

Runtime imports are standard-library modules except for three deliberate lazy
or optional paths:

- `cloudpickle` is attempted at runner import and falls back to `pickle`;
- TOML parsing tries standard-library `tomllib`, then optional `tomli`, then
  optional `tomlkit`; and
- IPython is imported only by the optional extension hook.

The source optional extras are:

```text
toml:        tomli; python_version < '3.11'
cloudpickle: cloudpickle; platform_python_implementation != 'PyPy'
```

The unpinned development group contains `setuptools>=68.0`, `build`, `twine`,
`pyflakes>=3.0`, `pycodestyle>=2.10`, `rut>=0.3`, `coverage>=7.0`, and the
conditional `tomli`. The documentation group separately contains Sphinx and
theme/extensions. No `uv.lock`, requirements lock, constraints file,
hash-pinned wheelhouse, or content-addressed dependency artifact is tracked at
this revision.

The current CI uses `uv sync --group dev`, then runs `doit pyflakes`, `doit
codestyle`, `rut -vv`, and one coverage job. Its matrix spans Ubuntu, Windows,
macOS, CPython 3.10-3.13, and PyPy 3.11. The older `DEV-README.rst` still says
`py.test`, while the current `dodo.py` and workflow use `rut`; a future command
plan must resolve this version drift explicitly. Pytest 9.1.1 was used only as
a compatible collect-only probe for this catalog and is not an upstream lock.

System and platform closure is also incomplete:

- `strace` is installed only for Ubuntu CI and gates six diagnostic tests;
- the default DBM implementation and file extensions vary by operating system
  and installed standard-library modules;
- shell command behavior depends on the shell, `PATH`, quoting, executable
  availability, process signals, and exit-code conventions;
- filesystem timestamp precision, `atime`/`ctime` meaning, permissions, case
  sensitivity, and path separators vary; and
- multiprocessing start method and pickling behavior differ by interpreter and
  operating system.

Consequently, "no runtime dependencies" does not mean the build/test/system
closure is known. The catalog correctly leaves dependency and environment
status unknown.

## Tests and Provisional Collection

The exact checkout has 27 `test*.py` modules, seven Python support/fixture
modules, and 673 source-level methods/functions whose names start with `test`.
Mixin inheritance expands those definitions into more effective cases,
especially for five storage backend variants and three runner variants.

Two independent controlled collection methods observed 891 unique nodes.

### Standard-library discovery

```text
environment: CPython 3.14.6
command shape: unittest.TestLoader.discover("tests")
strace probe: os.system patched to return 127; no external command run
cloudpickle: absent
collected: 891 unique cases
loader errors: 0
ordered/sorted ID SHA-256:
  6975df956d39ddb56c4c9e465953268bd54b27f9524a7c81841a469811823583
```

At import time six `test_cmd_strace` methods were marked skipped because the
controlled probe disabled `strace`; two `test_runner` methods were marked
skipped because `cloudpickle` was absent. MRunner and the UTF-8 locale checks
were available. The cases remain part of the observed collection.

### Pytest collect-only

```text
environment: CPython 3.12.11, pytest 9.1.1
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
PYTHONDONTWRITEBYTECODE=1
-p no:cacheprovider
PATH=/nonexistent (the import-time `strace -V` probe cannot resolve)
command: python -m pytest --collect-only -q tests
run 1: 891 nodes, exit 0
run 2: 891 nodes, exit 0
ordered node-list SHA-256 both runs:
  62de832215b10f5a455d8051028238ed563bb0ffda80a7271b47f59bb93fadeb
```

No test body was executed. The effective pytest module counts were:

| Module | Nodes | Module | Nodes |
| --- | ---: | --- | ---: |
| `test___init__` | 1 | `test___main__` | 1 |
| `test_action` | 100 | `test_api` | 4 |
| `test_cmd_base` | 28 | `test_cmd_clean` | 13 |
| `test_cmd_completion` | 8 | `test_cmd_dumpdb` | 1 |
| `test_cmd_forget` | 8 | `test_cmd_help` | 8 |
| `test_cmd_ignore` | 5 | `test_cmd_info` | 6 |
| `test_cmd_list` | 17 | `test_cmd_resetdep` | 9 |
| `test_cmd_run` | 14 | `test_cmd_strace` | 6 |
| `test_cmdparse` | 40 | `test_control` | 60 |
| `test_dependency` | 253 | `test_doit_cmd` | 20 |
| `test_exceptions` | 9 | `test_loader` | 55 |
| `test_plugin` | 9 | `test_reporter` | 32 |
| `test_runner` | 76 | `test_task` | 80 |
| `test_tools` | 28 | **total** | **891** |

This is useful source-shape evidence, not a frozen denominator. No final image,
optional dependency set, platform policy, pytest/rut policy, structured result,
skip policy, or private adapted suite exists. No full source baseline or Oracle
run was performed.

## CLI and Task-Runner Test Surface

The source suite is behavior-rich rather than metadata-only:

- `test_action` and `test_task` cover shell/list/callable actions, output
  capture, Unicode decoding, buffering, return classification, metadata
  arguments, task validation, cleanup, pickling state, parameters, and values;
- `test_dependency` expands backend mixins across JSON, SQLite, GNU DBM, NDBM,
  and dumb DBM, then covers signatures, target/file changes, ignore state,
  custom up-to-date callables/commands, and reason reporting;
- `test_control`, `test_runner`, and `test_cmd_run` cover dependency dispatch,
  setup/teardown, continuation, groups, `getargs`, serial/thread/process modes,
  queues, pickling, custom reporters, selection, and output files;
- loader/config/plugin tests cover dodo lookup and cwd changes, source-order
  discovery, generators, delayed tasks, task-creator parameters, TOML/INI
  merging, local plugins, installed entry-point shape, and error paths; and
- command modules cover list/help/info/clean/forget/ignore/reset-dep/dumpdb,
  bash/zsh completion, `python -m doit`, and conditional Linux `strace`.

Several tests import low-level command, parser, controller, backend, queue, and
runner objects and use in-process mocks. Preserving their assertions through a
separate candidate boundary is therefore a real adaptation task, not a simple
change from `pytest package` to `pytest candidate_client`.

## Timestamp and Filesystem Determinism

The core has deliberate timestamp-sensitive behavior:

- `MD5Checker` treats an identical mtime as unchanged without rehashing; a
  changed mtime with unchanged size falls through to MD5 comparison.
- `TimestampChecker` compares only mtime.
- `tools.check_timestamp_unchanged` exposes atime, ctime, or mtime and allows a
  caller-supplied comparator.
- `tools.timeout` uses wall-clock `time.time()` and persists a success time.
- `reporter.TaskResult` records start/finish wall-clock values and renders an
  absolute UTC timestamp plus elapsed seconds.

The source tests include a one-second sleep specifically to force an mtime
change and two 0.1-second sleeps around threaded output. These are sensitive to
filesystem granularity and scheduler load. A final verifier must use controlled
clock/mtime fixtures or tolerance-based state assertions; it must not compare
current timestamps or rely on sleeps for correctness.

Path and storage behavior also depends on cwd mutation, parent dodo search,
temporary directory permissions, case sensitivity, path separators, the
platform meaning of ctime, DBM availability/file extensions, and whether NDBM
can safely iterate/corruption-check. Those dimensions require an immutable
environment policy and explicit skips rather than opportunistic host behavior.

## Subprocess and Concurrency Determinism

Command strings run with `shell=True`; list actions run without a shell. Their
observable behavior depends on shell quoting, `PATH`, environment, executable
versions, encoding/locale, process signals, and platform return codes.
`CmdAction` captures stdout and stderr in separate reader threads and combines
the final logical result as stdout followed by stderr, not chronological
cross-stream order. Live output timing is scheduler-dependent.

The tests execute real subprocess paths for command actions and `python -m
doit`; the conditional strace suite invokes a Linux system binary. Up-to-date
strings also execute through the shell. Long-running/interactive actions can
outlive normal output capture unless an outer supervisor enforces process-tree
cleanup and time limits.

Parallel mode adds process/thread scheduling, queue timing, start-method, and
pickling differences. Without `cloudpickle`, closures and dynamic delayed task
creators may be invalid for multiprocessing while remaining valid in thread
mode. Independent task completion and live reporter order are intentionally not
stable. Deterministic verifier scenarios must assert dependency constraints and
final effects, not incidental parallel ordering.

## Plugin and Configuration Determinism

`PluginDict` combines local `module:attribute` configuration with
`importlib.metadata.entry_points()` results. Installed entry points override a
same-name local plugin. Therefore plugin availability and collisions depend on
the complete installed distribution metadata visible to the candidate process.
Plugin import executes arbitrary module code and caches the loaded object.

TOML behavior also depends on which parser wins the ordered fallback
`tomllib`, `tomli`, `tomlkit`. The final environment must contain an explicit
parser set and an isolated site-packages directory. Plugin tests should use
reviewed local fixture modules or prebuilt fixture distributions, disable
unrelated entry-point contamination, and avoid asserting unspecified metadata
iteration order.

Global command variables, task module imports, current directory,
`Globals.dep_manager`, and persisted `.doit.db` state can survive within a
process/workspace. Each scenario needs a fresh process unless it deliberately
tests a multi-command lifecycle, in which case only the scenario's isolated
workspace and state database should persist.

## Separate Candidate Boundary

The generic Python `candidate_client.call` accepts JSON-compatible arguments,
starts a fresh candidate child, imports one attribute, and requires a JSON-safe
result. It cannot represent the full upstream contract:

- task creators, actions, up-to-date checks, titles, cleanup hooks, reporters,
  codecs, checkers, commands, loaders, and plugins are live Python callables or
  classes;
- `Task`, action, failure, dependency status, parser, reporter, and backend
  instances retain process-local mutable state;
- tests pass file objects, temporary paths, mocks, queues, locks, processes,
  threads, exception objects, generators, and namespace modules;
- module loading and plugins intentionally execute Python code;
- run/list/info/clean/forget/reset workflows require state and files to persist
  across multiple candidate CLI invocations; and
- direct trusted imports or monkeypatching of candidate internals would violate
  the required separate-verifier policy.

The CLI is a viable boundary for a deliberately selected public subset. A
reviewed doit-specific adapter could receive declarative scenarios, create a
public fixture `dodo.py` and allowlisted helper modules inside an isolated
workspace, invoke the candidate's `python -m doit` in a child process, and
return bounded exit status, stdout, stderr, and a normalized filesystem/state
projection. Multi-command scenarios would retain only that isolated workspace.

That boundary still needs integrity controls because task actions can spawn
arbitrary commands and plugins can import arbitrary code. The future runner
must use an unprivileged child, no network, controlled `PATH`/`HOME` and
site-packages, read-only trusted fixture inputs, writable candidate output
paths, process/output/time limits, descendant cleanup, and trusted-side result
inspection. Hidden expected values and assertions stay outside the child.

Library and extension behavior not expressible through CLI fixtures requires a
reviewed child-side scenario vocabulary that reconstructs allowlisted
callables/classes and returns JSON-safe observations. No such adapter or
approved narrowed test contract exists here. The audit does not choose one
silently.

## Candidate Contamination Risk

The exact project, distribution name, repository, commit, and public package
are discoverable. An agent with unrestricted network access could download the
implementation instead of generating it from the instruction. The manifest
therefore records no-network as the intended benchmark mode, but no final image
or egress proof exists. A future experiment must state its network and public
package policy and must not compare a network-enabled run with an offline run
as though they measured the same task.

## Blockers and Reopen Conditions

Reopen this task only after all of the following are independently reviewed and
recorded:

1. Freeze Python, OS, base image digest, shell/core utilities, locale/timezone,
   filesystem behavior, multiprocessing start method, DBM modules, and the
   inclusion/exclusion policy for Linux `strace`.
2. Build a hash-locked offline dependency artifact for the selected build and
   verifier commands, including setuptools, pytest or rut as chosen, TOML and
   cloudpickle policy, and all transitive packages.
3. Approve a versioned public test scope and complete bidirectional
   test-to-spec traceability. Resolve direct internal imports, stale pytest
   documentation versus current rut CI, backend/platform variants, and
   skip/xfail semantics without deleting core behavior assertions.
4. Implement and review the task-specific subprocess/CLI scenario adapter,
   persistent-workspace protocol, process-tree containment, plugin isolation,
   and trusted result normalization.
5. Provision private tests, commands, and Oracle references through the
   authorized visibility-separated artifact store; do not copy those bytes into
   this catalog.
6. Collect in the final environment, freeze the structured denominator, and
   run three independent source/Oracle baselines with stable collection and
   `valid=true`.
7. Run empty, packaging/stub, forgery, and offline controls, followed by blind
   implementation and traceability review.
8. Record and enforce the public-source/package contamination policy before
   any model pilot or publication.

No Docker, Harbor, full source test, Oracle, control, private artifact
materialization, or shared-file mutation was performed by this static audit.

## Commands and Scope Evidence

Representative commands used for the evidence above were:

```text
git clone --no-checkout --filter=blob:none \
  https://github.com/pydoit/doit.git /tmp/nl2repo-doit-audit
git -C /tmp/nl2repo-doit-audit checkout --detach \
  1f9cbbce78a93f96a35abf2db5425361e2abf142
git -C /tmp/nl2repo-doit-audit show -s \
  --format='commit=%H%ntree=%T%nauthor_date=%aI%ncommitter_date=%cI%nsubject=%s'
git -C /tmp/nl2repo-doit-audit archive --format=tar HEAD
sha256sum <two temporary archives> LICENSE pyproject.toml
python3 <task-local AST/LOC/import/test-definition inventory>
python3 <controlled unittest discovery with os.system patched>
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 PATH=/nonexistent \
  <Python 3.12.11> -m pytest --collect-only -q -p no:cacheprovider tests
```

Archive generation and pytest collection were each repeated twice with matching
digests/counts. All temporary checkout/archive/probe material stayed outside
the worktree. Catalog validation and final diff/scope checks are reported by
the implementation handoff rather than being represented as an upstream
baseline.
