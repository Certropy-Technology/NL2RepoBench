# Project Description

Create a complete, installable Python project named `build` from an empty
workspace. The project is a small PEP 517 frontend: it reads a local
`pyproject.toml`, asks the declared build backend for metadata or distributions,
and writes wheel or source distribution files into a caller-selected directory.
The implementation must be local and deterministic for the documented inputs.

The package is imported as `build`. Its public root export is
`build.ProjectBuilder`; the public helper modules are `build.env` and
`build.util`. The command-line entry point is provided by `python -m build` and
by the `pyproject-build` console script. Do not implement an unrelated package
installer, dependency resolver, remote repository client, or test runner.

# Natural Language Instruction

Build the `build` package from scratch in `workspace/`. Produce a normal PEP 517
project with install metadata and a usable `build/` Python package. Preserve the
public import paths, signatures, result shapes, filesystem effects, and error
boundaries in this document.

Required capabilities:

1. Expose `build.ProjectBuilder` at the package root and implement its builder
   discovery, source directory, Python executable, requirement inspection,
   metadata preparation, and distribution build operations.
2. Implement the public isolated-environment protocol in `build.env`, including
   the properties and methods needed by a backend invocation.
3. Implement `build.util.project_wheel_metadata` and the documented wheel
   filename parser behavior without importing candidate implementation code.
4. Provide the `pyproject-build` and `python -m build` command interfaces with
   wheel/source-distribution selection, output directory selection,
   dependency-check control, and nonzero failures.

Do not copy a source checkout or its tests. Keep package behavior deterministic,
avoid network access at runtime, and make every public entry point usable from
the directory structure below. If a backend needs an unavailable dependency,
report that through the documented exception or CLI failure rather than silently
contacting an index.

# Supports

- Support CPython 3.8 and newer Python 3.x versions compatible with build 1.2.2;
  the evaluation runtime is CPython 3.12.
- Use a PEP 517/518 `pyproject.toml` and expose package metadata for the
  distribution name `build`.
- Runtime dependencies are `packaging` and `pyproject_hooks`; platform-specific
  compatibility dependencies may be declared when they are actually needed.
  Build backends such as Flit or Setuptools are build-time concerns, not APIs
  to invent in this package.
- The task environment is NoNetwork. Agent, candidate, verifier, Oracle, and
  controls must not access GitHub, PyPI, npm, Go proxy, DNS, or external
  services during execution. Required packaging tools and local backend
  artifacts must be installed during image construction.
- A local project directory, a local `pyproject.toml`, and a writable output
  directory are valid inputs. Paths may be relative or absolute, but output
  paths must resolve to the requested directory and must not be replaced by a
  network cache.

# Project Directory Structure

```text
workspace/
├── pyproject.toml
├── README.md
├── LICENSE
└── build/
    ├── __init__.py
    ├── __main__.py
    ├── env.py
    ├── util.py
    ├── _builder.py
    ├── _ctx.py
    ├── _exceptions.py
    ├── _types.py
    └── py.typed
```

`build.ProjectBuilder` must be importable from `build`, while
`build.env.IsolatedEnv`, `build.env.DefaultIsolatedEnv`, and
`build.util.project_wheel_metadata` remain importable from their named modules.
The executable entry point must resolve to `build.__main__:entrypoint`, and
`python -m build` must invoke the same CLI implementation.

# API Usage Guide

## `build.ProjectBuilder`

Import path: `from build import ProjectBuilder`.

Constructor signature:

```python
ProjectBuilder(
    source_dir,
    python_executable=sys.executable,
    runner=pyproject_hooks.default_subprocess_runner,
)
```

`source_dir` is a path-like string naming a directory containing a readable
`pyproject.toml`. The constructor stores its absolute source path, reads the
`build-system` table, and selects its `build-backend` and optional
`backend-path`. A missing source directory, malformed TOML, missing backend
field, or non-directory path raises an appropriate build or filesystem error;
do not treat such input as an empty project.

`python_executable` is the executable used for backend hook calls and is exposed
by the `python_executable` property as a string. `runner` is a callable accepting
`(cmd, cwd, extra_environ)` and is used for backend subprocesses. A custom runner
is useful for deterministic observation and must receive the source directory as
its working directory. Constructing a builder has no network side effect.

Properties:

- `source_dir -> str`: absolute source directory; repeated reads are equal.
- `python_executable -> str`: selected Python executable string.
- `build_system_requires -> set[str]`: declared `build-system.requires`, or the
  package's documented defaults when the build-system table is absent. The set
  has no meaningful ordering.

`ProjectBuilder.from_isolated_env(env, source_dir, runner=...) -> ProjectBuilder`
is a class method. `env` supplies `python_executable` and
`make_extra_environ()`. The returned builder invokes hooks with the isolated
interpreter and merged environment. It does not mutate the caller's source
files merely by construction.

`get_requires_for_build(distribution, config_settings=None) -> set[str]` calls
the backend's `get_requires_for_build_<distribution>` hook. `distribution` is
`"wheel"` or `"sdist"`; `config_settings` is a mapping or `None`. The result
is a set of PEP 508 requirement strings. A backend failure is reported as a
`build.BuildBackendException`, not converted to an empty set.

`check_dependencies(distribution, config_settings=None) -> set[tuple[str, ...]]`
combines declared build-system requirements with backend requirements and
returns unmet dependency paths. Each tuple contains one or more requirement
strings, including ancestral requirements where applicable. Satisfied
requirements produce an empty set. Invalid requirement syntax or a backend
failure is an error, not a successful check.

`prepare(distribution, output_directory, config_settings=None) -> str | None`
prepares metadata and is intended for `distribution="wheel"`. It returns the
absolute path to the generated `.dist-info` metadata directory when the backend
supports the preparation hook, or `None` when that hook is unavailable. The
output directory is created if needed. Backend failures raise
`BuildBackendException`.

`build(distribution, output_directory, config_settings=None,
metadata_directory=None) -> str` calls the matching PEP 517 backend hook and
returns the absolute path to the emitted artifact. `distribution` is `"wheel"`
or `"sdist"`. `metadata_directory`, when supplied, is a path returned by a
previous `prepare` call. The output directory is created when absent and must
remain a directory; a conflicting file raises `BuildException`.

`metadata_path(output_directory) -> str` returns a metadata directory. It first
uses `prepare("wheel", ...)`; when unavailable it builds a wheel, extracts the
matching `.dist-info` members, and returns that directory. The returned path is
inside the requested output directory. Invalid wheel names and backend failures
are errors.

## `build.util`

`from build.util import project_wheel_metadata`.

`project_wheel_metadata(source_dir, isolated=True, *,
runner=pyproject_hooks.quiet_subprocess_runner) -> importlib.metadata.PackageMetadata`
returns package metadata for the wheel produced by a local project. With
`isolated=True`, it creates an isolated environment, installs the declared
build requirements, and invokes metadata preparation. With `isolated=False`, it
uses the current environment. The result supports mapping-style metadata
access such as `metadata["Name"]` and `metadata["Version"]`. The helper may
launch subprocesses and write temporary files; it must clean those files before
returning. Missing preinstalled backends or malformed projects raise a build
backend exception rather than causing a network fetch.

`build.util` in version 1.2.2 publicly exposes the metadata helper. The frozen
1.2.2 AST inventory contains the wheel filename parser at
`build._util.parse_wheel_filename`; it returns `re.Match[str] | None` and is
described here as an observable parser contract, not as a requirement to expose
the underscore module as a public root API. For a filename matching
`<distribution>-<version>[-<build>]` followed by Python, ABI, and platform tags
and `.whl`, the match exposes the named groups `distribution`, `version`,
optional `build_tag`, `python_tag`, `abi_tag`, and `platform_tag`. A nonmatching
filename returns `None`. Do not invent a `parse_sdist_filename` export: it is
not present in the frozen 1.2.2 source AST surface.

`build.check_dependency(req_string, ancestral_req_strings=(),
parent_extras=frozenset())` is re-exported at `build.check_dependency`. It yields
an iterator of unmet dependency paths. Requirement markers and extras are
considered, already-seen ancestral requirements stop cycles, and installed
compatible distributions are followed through their declared requirements.
The output is deterministic for a fixed environment; malformed requirement
strings raise the dependency parser's error.

## `build.env`

`IsolatedEnv` is a protocol with properties/methods
`python_executable -> str` and `make_extra_environ() -> Mapping[str, str] | None`.
An implementation supplies the interpreter used for backend calls and optional
additional environment variables. It does not prescribe an installation
backend by itself.

`DefaultIsolatedEnv(*, installer="pip") -> DefaultIsolatedEnv` supports the
installers `"pip"` and `"uv"`. As a context manager, `with DefaultIsolatedEnv()
as env:` creates a temporary isolated environment, exposes `env.path` and
`env.python_executable`, and removes the environment on exit. `env.path -> str`
is the temporary environment location, and `env.make_extra_environ() -> dict`
returns a PATH adjustment containing its scripts directory.

`env.install(requirements: Collection[str]) -> None` installs the supplied PEP
508 requirement strings into the isolated environment. An empty collection is
a no-op. Installation launches a subprocess and can fail with
`FailedProcessError`; under this task's NoNetwork policy, tests must not require
an index or an unavailable package. Environment creation and installation are
therefore documented but not treated as an offline-safe hidden behavior.

# Implementation Notes

Preserve the distinction between source inspection, backend subprocess errors,
and dependency installation errors. Backend hooks receive the selected source
working directory, configuration settings, and any metadata directory exactly
once per requested operation. Do not make a second network attempt after a
failure.

Wheel and source-distribution builds write artifacts into the caller's output
directory and return paths, not bare filenames. Repeated parser calls with the
same filename return equivalent groups. Do not rely on dictionary ordering for
requirement sets, and do not include temporary environment paths in public
metadata.

The command-line frontend should delegate to the same builder behavior. The
`--sdist` and `--wheel` flags select requested distributions, `-o`/`--outdir`
selects the output directory, and `--skip-dependency-check` bypasses the
pre-build unmet-dependency check. Successful builds print a concise `Built ...`
message to stdout and exit zero. Invalid options, missing projects, dependency
failures, backend failures, or artifact failures exit nonzero and report an
explanation on stderr.

# Examples

## Normal example: parse a wheel name

```python
from build._util import parse_wheel_filename

match = parse_wheel_filename("demo_pkg-1.2.3-py3-none-any.whl")
assert match is not None
assert match.group("distribution") == "demo_pkg"
assert match.group("python_tag") == "py3"
```

## Normal example: inspect a local builder

```python
from build import ProjectBuilder

builder = ProjectBuilder("sample-project")
assert builder.source_dir.endswith("sample-project")
assert isinstance(builder.build_system_requires, set)
```

## Normal example: build with a preinstalled local backend

```python
from pathlib import Path
from build import ProjectBuilder

out = Path("dist")
out.mkdir(exist_ok=True)
artifact = ProjectBuilder("sample-project").build("wheel", out)
assert Path(artifact).is_file()
assert artifact.endswith(".whl")
```

## Normal example: read project metadata

```python
from build.util import project_wheel_metadata

metadata = project_wheel_metadata("sample-project", isolated=False)
assert metadata["Name"]
assert metadata["Version"]
```

# Error Handling and Boundary Conditions

- `parse_wheel_filename("not-an-artifact.txt")` returns `None`; it must not
  guess a distribution from an arbitrary suffix.
- A source path without `pyproject.toml`, or with a malformed build-system
  table, raises a build/configuration error. Do not silently use a different
  directory or backend.
- Passing an output path that is an existing regular file to `build()` raises
  `BuildException` (or a documented subclass) and leaves that file intact.
- An unsupported distribution string such as `"zip"` fails explicitly; it must
  not be treated as a wheel or sdist.
- An unavailable backend, invalid configuration setting, or nonzero backend
  subprocess is surfaced as `BuildBackendException` with its underlying failure
  available for diagnostics.
- `DefaultIsolatedEnv.install()` can require pip/uv and package artifacts. Do
  not add tests that contact a package index. If those artifacts are not
  preinstalled in the production image, classify the isolated-install scenario
  as an environment limitation rather than weakening the pure API contract.
- Tests may assert local file existence, return types, parser groups, metadata
  fields, deterministic repeated calls, and CLI exit behavior. They must not
  assert hidden implementation names, private state layout, temporary path
  spelling, or network-dependent build success.
