# `typer` Static Authoring Audit

Status: **blocked**. This directory contains public audit evidence only. It
does not contain a task descriptor, public instruction projection, copied
upstream tests, hidden assertions, private command plan, dependency wheels,
Docker or Harbor files, verifier code, Oracle solution, secrets, or shared
catalog/dataset edits. No legacy task exists at `test_files/typer/`.

## Decision

Do not publish a task from this lane. The requested source revision is exact,
the project license is MIT, the source archive is reproducible, and a
source-only Linux collection probe is stable. Those facts do not complete the
production authoring contract:

- the archive also contains an adapted Click 8.3.1 implementation with a
  retained BSD-3-Clause notice;
- the committed lock names and hashes registry artifacts, but no authorized
  offline wheelhouse exists and the unpinned PDM build backend is not in that
  lock;
- the effective suite and pass/skip/xfail behavior depend on OS, interpreter,
  dependency resolution, shell detection, terminal settings, completion
  permissions, subprocess tools, and xdist policy; and
- most tests construct typed callbacks and `Typer`/`CliRunner` objects inside
  pytest. The generic JSON candidate client cannot carry those Python objects
  or preserve their process-local state, while the generic module/console
  operations cover only already-installed executable entry points.

The CLI surface is a plausible future subprocess task, but faithfully
adapting the full upstream suite requires a Typer-specific child scenario
adapter and an explicit platform policy. Direct candidate imports from trusted
pytest are not an acceptable fallback.

## Candidate Identity And Exact Source

The candidate is the `typer` entry in
`reports/python-package-candidates.v1.json`:

- repository: `https://github.com/fastapi/typer`;
- discovery category: CLI;
- discovery license: MIT;
- requested and resolved revision:
  `9a7b2e83f6b62c750d6026b0de9ebf2026a8b8fa`;
- commit tree: `ee7dfae29184d7a3989bde4df59d68dff52118f0`;
- parent: `31f30d721335d3f4280855812e439c61b6560376`;
- author and committer time: `2026-08-12T07:20:13Z`;
- subject: `Update release notes` (the source subject includes a leading
  documentation emoji, omitted here to keep this artifact ASCII);
- submodules: none; and
- detached checkout: clean before and after audit cleanup.

The source lock was generated directly from that detached commit without a
prefix or repack:

```text
command:         git archive --format=tar HEAD
archive members: 916 (including directory entries)
archive bytes:   2,723,840
archive sha256:  4713273f314d75895e287e1dfed01cd97d1d1c6ec643ebb9e379ff5e80dda71b
```

Two independent archive commands produced the same size and digest. The tar
files and detached checkout remain temporary audit material outside this
repository. No source or archive bytes were copied into the catalog.

No pre-existing `catalog/tasks/typer/`, `test_files/typer/`, or normalized
task-ID duplicate was found before this record was created.

## License Evidence

The project-level license evidence is internally consistent:

- `LICENSE` is 1,086 bytes and 21 newline-terminated lines;
- Git blob: `a7694736cf37716aafec14b24aa8d6316ebe07a3`;
- SHA-256:
  `58992cebcf8dfb6e40c4e2112ed12126c243666dca3912a3d78b7ecac4859d49`;
- its text is the MIT permission, warranty, and liability license; and
- `pyproject.toml` declares `license = "MIT"` and includes `LICENSE` in the
  built distribution.

The runtime package vendors and adapts Click under `typer/_click/` and states
that it is based on Click 8.3.1. Its separate notice must also be preserved:

- `typer/_click/LICENSE.txt` is 1,475 bytes and 28 newline-terminated lines;
- Git blob: `d12a849186982399c537c5b9a8fd77bf2edd5eab`;
- SHA-256:
  `9a8ad106a394e853bfe21f42f4e72d592819a22805d991b5f3275029292b658d`;
- its text is the BSD 3-Clause license with Pallets copyright; and
- the temporary wheel retained both the project MIT license and this vendored
  notice.

Thus MIT correctly describes Typer's project metadata, but a future source or
runtime artifact must not erase the bundled BSD-3-Clause attribution or imply
that every archived implementation byte has only the MIT notice.

## Package, Build, And Size

`pyproject.toml` and the runtime source identify:

- distribution and import package: `typer`;
- version: `0.27.1`, read dynamically by PDM from `typer/__init__.py`;
- supported Python metadata: `>=3.10`;
- build backend: `pdm.backend` with the unversioned requirement
  `pdm-backend`;
- console entry point: `typer = typer.cli:main`;
- module entry point: `python -m typer` delegates to the same CLI;
- typed package markers: `typer/py.typed` and `typer/_click/py.typed`; and
- package-local agent guidance: `typer/.agents/skills/typer/SKILL.md`, which
  is runtime wheel data and would need an explicit publication/contamination
  policy rather than being silently dropped.

Tracked runtime implementation counts from the exact source are:

| tree | Python files | physical | nonblank | nonblank/non-leading-comment |
| --- | ---: | ---: | ---: | ---: |
| all `typer/**/*.py` | 31 | 13,905 | 11,781 | 11,023 |
| `typer/_click/**/*.py` | 15 | 5,576 | 4,495 | 4,193 |
| Typer code excluding bundled Click | 16 | 8,329 | 7,286 | 6,830 |

The complete implementation is in the original Hard LOC band. This is not a
small wrapper around an external Click install: the adapted Click parser,
command, formatting, termui, shell-completion, and Windows-console modules are
part of the candidate behavior.

A temporary wheel build was used only as a packaging sanity check:

```text
file:       typer-0.27.1-py3-none-any.whl
bytes:      122,400
members:    40
sha256:     ebee8408fb0468132d5173d66b74a7ddd65d8e042ba6a74dd9d2c06f6125e13c
generator:  pdm-backend 2.4.9
entrypoint: typer = typer.cli:main
```

The wheel metadata reproduced the version, Python requirement, four direct
runtime requirements, MIT expression, and project license file. The wheel is
not stored here and is not an approved source, dependency, or Oracle artifact.
It was built with the host's available build cache/index state, not a clean
content-addressed offline build.

## Typed Application And CLI Behavior

The root package exposes the application-building API (`Typer`, `Option`,
`Argument`, `run`), execution and terminal helpers (`echo`, `secho`, `style`,
`prompt`, `confirm`, `getchar`, `progressbar`, `launch`), context and callback
types, text/binary file types, and Click-derived exceptions. `Typer` retains
live Python callbacks and group/application objects. Its decorators register
functions and defer conversion to the adapted Click command graph.

The typed behavior reviewed in source and tests includes:

1. Function signatures and `typing.Annotated` metadata determine arguments,
   options, required/default/default-factory behavior, names, help, prompts,
   environment variables, callbacks, and completion callbacks.
2. Supported conversions include scalar strings, integers, floats, booleans,
   UUIDs, datetimes, `Literal`, enums, optional values, lists, fixed tuples,
   paths, and text/binary files. Path and enum values are converted back into
   Python objects before the user callback runs.
3. Callers may supply arbitrary Python callback/default/parser functions,
   custom Click `ParamType` instances, application/group subclasses, result
   callbacks, context settings, and nested `Typer` applications.
4. Command construction inspects callback names, docstrings, annotations, and
   defaults, produces a live Click command graph, and wraps callback execution
   with context and type converters.
5. Rich help/error/traceback rendering depends on markup mode, terminal width,
   color/terminal detection, environment variables, and exact Rich behavior.
6. Completion detects the current shell through shellingham, renders
   Bash/Zsh/Fish/PowerShell scripts, writes shell profile files, and can invoke
   PowerShell. `launch()` can invoke `open`, `xdg-open`, or platform browser
   behavior.
7. The installed `typer` meta-CLI imports an application from a Python file or
   module, discovers a `Typer` object or callable, runs it, and can generate
   Markdown command documentation. This imports and executes user module code;
   it is not merely a pure argument-to-JSON transformer.

These behaviors are observable API contracts, not implementation directions
for a future instruction. They also explain why the full application surface
cannot be reduced to independent calls such as `call("typer", "Typer")`.

## `CliRunner` Contract

`typer.testing.CliRunner` is a project-owned runner derived from Click rather
than a re-export of an external Click test helper. Its relevant behavior is:

- `invoke(app, args, input, env, catch_exceptions, color, **extra)` accepts a
  live `Typer` object and converts it to a live Click command;
- string arguments are split with `shlex`, while sequences are used directly;
- invocation temporarily replaces `sys.stdin`, `sys.stdout`, `sys.stderr`,
  environment values, prompt/getchar functions, ANSI stripping, and formatter
  width, then restores them;
- the class explicitly documents that this global-state isolation is only
  suitable for single-threaded use;
- stdout and stderr are captured separately and in a mixed output stream;
- CRLF is normalized in the text properties; and
- `Result` retains byte streams, decoded streams, arbitrary callback return
  value, exit code, exception instance, and `exc_info` traceback tuple.

Those inputs and outputs are Python-rich and stateful. `Typer`, callbacks,
classes, `Context`, Click parameters, file handles, exception/traceback
objects, and arbitrary return values are not JSON values. Splitting app
construction and invocation across fresh subprocesses also changes the
contract.

Static test inspection found **612** `*.invoke(...)` calls across **167** test
files. The tests repeatedly define callback functions/classes in the pytest
process, register them on apps, invoke the same app, inspect live command and
parameter objects, patch candidate globals, and assert `Result` fields. This
is the dominant test shape rather than an edge case.

## Test Inventory And Collection

The exact source contains:

- 296 Python files under `tests/`;
- 208 `test_*.py` modules;
- 958 static `test*` function definitions after nested AST traversal;
- 304 Python examples under `docs_src/`, many imported or launched by tutorial
  tests; and
- 309 static `subprocess.run` calls plus one `subprocess.Popen` call across
  186 test files.

The discovery report did not provide a Typer test denominator. Static
definition counts are not used as one.

A source-only, cache-disabled collection probe was run with candidate code on
`PYTHONPATH`, pytest plugin autoload disabled, and these versions selected from
the committed lock: pytest 9.1.1, Rich 15.0.0, shellingham 1.5.4,
annotated-doc 0.0.4, markdown-it-py 4.0.0, mdurl 0.1.2, Pygments 2.20.0,
iniconfig 2.3.0, packaging 25.0, and pluggy 1.6.0.

The command shape was:

```text
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
PYTHONPATH=<detached-source> \
uv run --no-project --python <interpreter> \
  --with pytest==9.1.1 --with rich==15.0.0 \
  --with shellingham==1.5.4 --with annotated-doc==0.0.4 \
  --with markdown-it-py==4.0.0 --with mdurl==0.1.2 \
  --with pygments==2.20.0 --with iniconfig==2.3.0 \
  --with packaging==25.0 --with pluggy==1.6.0 \
  python -m pytest --collect-only -q -p no:cacheprovider tests
```

| Interpreter | Runs | Collected | Collection errors | Node-list SHA-256 |
| --- | ---: | ---: | ---: | --- |
| CPython 3.12.11 Linux | 1 | 1,399 | 0 | `75ea4178af9df577acad620b0538c7646eddf693bf9a0f66b641ba6b0c1d46a6` |
| CPython 3.13.14 Linux | 1 | 1,399 | 0 | same |
| CPython 3.14.6 Linux | 2 | 1,399 | 0 | same |

The normalized list has 1,399 lines and 121,882 bytes. All four lists are byte
identical. Its directory breakdown is:

```text
tests/test_tutorial/     930
tests/ root modules      323
tests/test_completion/    84
tests/test_cli/           62
                         ----
                         1399
```

This is reproducible **collection evidence only**. No test body was executed,
no JUnit was produced, and the 1,399 count is not a frozen production
denominator.

The upstream execution policy is materially different from this minimal
collection probe. `scripts/test.sh` sets `TERMINAL_WIDTH=3000`, forces terminal
detection off, grants completion-install tests permission, enables coverage,
and runs pytest with `--numprocesses=auto`. The pytest config uses strict
configuration/markers, warnings-as-errors, and strict xfail. Platform and
environment markers gate Linux, macOS, Windows, Rich, Bash, and completion
installation behavior. A final metric must select and record skip/xfail/xpass
semantics instead of inferring pass counts from collection.

Upstream CI has seven OS/interpreter/resolution jobs: Python 3.14 on Linux,
Windows, and macOS; Linux 3.10 with lowest-direct resolution; macOS 3.11 with
highest resolution; macOS 3.12 with lowest-direct resolution; and Windows 3.13
with highest resolution. A Linux-only node list cannot establish behavioral
parity for that matrix.

## Rich, Shellingham, And Windows Closure

The exact `pyproject.toml` declares this runtime dependency graph:

```text
annotated-doc >=0.0.2
rich >=13.8.0
shellingham >=1.3.0
colorama; platform_system == "Windows"
```

The committed `uv.lock` is 366,255 bytes with SHA-256
`a1df59386fbfbec671268b0779fb829a91ebf5f9e26c7c0a6ce79f55ec69ba02`
and Git blob `ca904ce69e680c3f187460fa2ec48559a02bdd49`. It contains 86 package
records across all groups and selects this runtime closure for current
supported environments:

```text
annotated-doc 0.0.4
rich 15.0.0
  markdown-it-py 4.0.0
    mdurl 0.1.2
  pygments 2.20.0
shellingham 1.5.4
colorama 0.4.6 (Windows)
```

The test group additionally selects coverage 7.13.1, mypy 2.3.0, pytest
9.1.1, pytest-cov 7.1.0, pytest-sugar 1.1.1, pytest-xdist 3.8.0, Ruff 0.16.0,
and ty 0.0.63 plus their transitive requirements. Python 3.10 adds backport
requirements such as exceptiongroup and tomli; Windows adds Colorama paths.

The lock records registry URLs and artifact hashes, but it is not a
materialized dependency bundle. Two clean-cache no-network probes failed
closed as expected:

1. `uv sync --frozen --offline --no-dev --group tests` failed because the
   locked mypy wheel was not present in the empty cache.
2. `uv build --offline --wheel` failed because `pdm-backend` was not present.
   More importantly, that build requirement has no version bound and no
   package record in `uv.lock`; the successful temporary build happened to use
   PDM backend 2.4.9.

The component-specific closure risks are:

- **Rich:** help, errors, markup, progress, and tracebacks depend on Rich plus
  its Markdown/Pygments chain. Tests deliberately change terminal width,
  terminal/color environment, markup mode, ANSI handling, and import timing.
  Allowing a resolver to advance only transitive packages can change rendered
  bytes even when direct requirements remain fixed.
- **shellingham:** shell completion imports it unconditionally and calls
  `detect_shell()`, which observes the process tree/environment. Tests also
  require Bash in some paths and mock PowerShell invocations. The shell and
  executable environment are part of the behavior lock, not just Python
  wheels.
- **Windows:** the direct Colorama marker supports ANSI streams, while the
  bundled Click code contains `ctypes`/WinAPI console readers and writers.
  `tests/test_win_console.py` is wholly Windows-gated, and other tests contain
  Windows-specific path, stream, encoding, launch, and completion branches.
  These cannot be validated by changing `sys.platform` in a Linux verifier.

A production closure therefore needs a selected OS/interpreter policy, all
runtime and test wheels with hashes, the PDM build backend, required shell
executables/system behavior, and a clean-cache offline replay. The current
lock and local uv cache are useful provenance but do not satisfy that gate.

## JSON And CLI Adapter Audit

The production Python boundary is implemented by
`src/nl2repobench/verification/candidate_client.py` and
`candidate_runner.py`:

- `call()`/`get()` JSON-encode one module/attribute request, start a fresh
  unprivileged child, and require one JSON-serializable response;
- `run_module()` executes an installed module with string arguments and can
  provide stdin text;
- `run_console()` locates exactly one installed console entry point and
  executes it with string arguments, but its public wrapper does not provide
  stdin or per-call environment overrides; and
- every operation has a fresh process, bounded output/resources, and no
  persistent object handles.

This boundary can check package metadata, selected JSON-safe pure helpers, and
the installed `typer` meta-CLI's ordinary module/console output. It cannot
transparently preserve the upstream suite:

1. `Typer()` and `main.get_command()` return live application/Click objects;
   `Option()` and `Argument()` return metadata objects; none is a JSON result.
2. Apps are built from live decorated callback functions, annotations, enums,
   custom parsers/types, nested groups, and context/result/completion
   callbacks. These cannot be sent as JSON arguments.
3. `CliRunner.invoke()` needs the app object in the same process and returns a
   `Result` containing arbitrary return values, exception/traceback objects,
   and byte streams.
4. Repeated invocations, command registration, monkeypatching, environment
   changes, module caches, and completion state are process-local. One fresh
   generic call per assertion loses that state.
5. Tests create files, import hundreds of `docs_src` modules, execute Python
   scripts, feed prompt/terminal input, inspect subprocess streams, and patch
   candidate internals. The console wrapper has no fixture/scenario protocol
   for these operations.
6. Real Windows console and shell-completion behavior needs a matching OS and
   controlled external executables; a JSON normalization layer alone cannot
   emulate it faithfully.

A future Typer-specific child adapter should accept a reviewed declarative
scenario rather than arbitrary Python source. Inside the untrusted candidate
child it must construct allowlisted callback signatures/annotations, option
and argument metadata, enums and nested apps; execute one or more invocations;
control stdin, environment, terminal width/color, filesystem fixtures, shell
detection, and selected platform mode; and return JSON-safe observations for
stdout, stderr, mixed output, exit code, callback arguments/return projection,
normalized exception details, generated help/completion text, and approved
file effects. Rich and Windows snapshots need explicit normalization and
platform-specific baselines.

Hidden expected values and assertions must remain in the trusted private
bundle. The child adapter must not expose hidden test bytes or accept arbitrary
trusted code for execution. No such adapter or approved narrowed CLI-only
contract exists in this lane.

## Blockers And Reopen Conditions

Keep `typer` blocked until all of the following are separately approved and
recorded:

1. A source/license policy that preserves both Typer's MIT license and the
   bundled Click BSD-3-Clause notice.
2. A final OS/Python/shell/terminal policy, including a decision on real
   Windows coverage and the upstream lowest/highest dependency matrix.
3. A complete hash-locked offline build/runtime/test closure containing the
   PDM backend, Rich chain, shellingham, Windows Colorama path, pytest tooling,
   and required system executables.
4. An authorized private test bundle and allowlisted command plan; do not copy
   upstream tests or `docs_src` fixtures into this public task directory.
5. A reviewed Typer-specific child scenario/CLI adapter that preserves typed
   callbacks, app construction, `CliRunner`, Rich, completion, filesystem,
   repeated-invocation, and platform behavior without trusted candidate
   imports.
6. Fresh structured collection in the final verifier with an explicit
   skip/xfail/xpass policy and frozen denominator.
7. Three independent valid Oracle runs followed by empty, stub, forgery, and
   clean-cache offline controls in a later execution lane.

## Static Commands And Scope

The audit used a detached public checkout and temporary files under `/tmp`:

```text
git clone --filter=blob:none --no-checkout https://github.com/fastapi/typer.git <tmp>
git checkout --detach 9a7b2e83f6b62c750d6026b0de9ebf2026a8b8fa
git show -s --format=... HEAD
git submodule status
git archive --format=tar HEAD (twice)
sha256sum <archives> LICENSE typer/_click/LICENSE.txt pyproject.toml uv.lock
AST/line/import/invocation/subprocess inventory over typer/, tests/, docs_src/
uv tree --locked --no-dev --group tests for Linux/Windows marker projections
python -m pytest --collect-only ... (CPython 3.12, 3.13, and 3.14 only)
uv build --python /usr/bin/python3 --wheel --out-dir <tmp> <source>
UV_CACHE_DIR=<empty> uv sync --frozen --offline --no-dev --group tests
UV_CACHE_DIR=<empty> uv build --offline --wheel <source>
```

No test body, full baseline, JUnit run, Docker build, Harbor job, Oracle,
negative control, hidden/private artifact materialization, secret access,
or shared catalog/index operation was performed. Public network access was
used to clone the public source and may have been used by temporary
non-offline package/build resolution; it used no credential or private
service. Temporary PDM build state was removed from the source checkout, which
ended clean. The only repository file created by this audit is this task-local
`blocked.md`.
