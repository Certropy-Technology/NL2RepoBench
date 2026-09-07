# Build `coverage`

```text
workspace/
├── pyproject.toml
└── coverage/
    ├── __init__.py
    ├── control.py
    ├── data.py
    ├── report.py
    └── __main__.py
```

Create a complete, installable Python project named `coverage` from an empty
workspace. It is a local code-coverage measurement library and command-line
tool. The project must work without network access at runtime and must not
depend on an installed copy of `coverage`.

## Project Description

Implement the public behavior of coverage.py release `7.16.0a0.dev1` for the
deterministic contract below. The library records executed Python source lines
and optional branch arcs, persists data in a SQLite-backed `.coverage` file,
combines parallel data files, and renders text, JSON, XML, LCOV, HTML, and
annotated-source reports. It also exposes plugin protocol base classes and the
`coverage` command module.

## Natural Language Instruction

Create `coverage` from an empty workspace. Implement local Python tracing,
SQLite-backed data, reporting, plugin protocols, and the command line API
specified below, with deterministic ordering and no runtime services.

## Supports or Environment Configuration

- Support CPython 3.10 or newer on Linux. A pure-Python tracer is sufficient;
  a native extension is optional and must not be required for installation or
  ordinary operation.
- Provide an installable top-level package named `coverage`, the module
  `coverage.__main__`, and the console entry point `coverage`.
- Use only the Python standard library at runtime. Build tools may be declared
  separately, but the finished package must import in an environment without
  third-party packages.
- Keep normal measurement, data access, reporting, and CLI operations local.
  Do not contact a network or require a service, database server, browser, or
  shell command from library APIs.
- Preserve deterministic ordering of returned file names, line numbers,
  contexts, and serialized report structures.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
└── coverage/
    ├── __init__.py
    ├── control.py
    ├── data.py
    ├── report.py
    └── __main__.py
```

## API Usage Guide

### Root exports

`coverage` must export `Coverage`, `CoverageData`, `CoverageException`,
`CoveragePlugin`, `FileTracer`, `FileReporter`, `CodeRegion`,
`coverage.__version__`, and `coverage.version_info`. The exception exported at
the root and from `coverage.exceptions` must be the same object.

### `coverage.Coverage`

Implement the documented constructor:

```python
Coverage(
    data_file=".coverage", data_suffix=None, cover_pylib=False,
    auto_data=False, timid=False, branch=False, config_file=True,
    source=None, source_pkgs=None, source_dirs=None, omit=None, include=None,
    debug=None, concurrency=None, check_preimported=False, context=None,
    messages=False, plugins=None,
)
```

`start()` begins tracing the current thread and `stop()` ends it. `save()`
writes collected data, `erase()` removes the data file, and `load()` reads an
existing file. `get_data()` returns a `CoverageData` object. `collect()` is a
context manager equivalent to start/stop. `current()` returns the most
recently started instance or `None` outside a collection.

`switch_context(label)` changes the active dynamic context while tracing.
`analysis(filename)` returns the standard analysis tuple, including the
missing-line representation. `report(file=..., morfs=..., omit=...,
include=..., ignore_errors=...)` returns a percentage and may write a text
report. `json_report`, `xml_report`, `lcov_report`, `html_report`, and
`annotate` produce their respective reports and return the measured percentage
where the upstream API does so. Report writers must create their requested
output files/directories and use stable data.

### `coverage.CoverageData`

`CoverageData(data_file=".coverage", basename=False, suffix=None,
no_disk=False, debug=None, warn=None)` stores line or arc data. Use
`add_lines(mapping)`, `add_arcs(mapping)`, `set_context(label)`, `set_query_context(label)`,
`set_contexts_by_lineno(mapping)`, `write()`, and `read()` for persistence and
updates. `lines(filename)`, `arcs(filename)`, `contexts_by_lineno(filename)`,
`measured_files()`, `measured_contexts()`, `has_arcs()`, `file_tracer(filename)`,
and `file_tracers()` return the corresponding data. `update(other)` merges
compatible data and rejects incompatible line/arc modes.

Line and arc collections are sets or lists according to the public API; callers
must receive the same values after a write/read round trip. Missing data files
and invalid operations raise the package's documented coverage exceptions,
not silent success.

### Plugin protocol

`CoveragePlugin`, `FileTracer`, and `FileReporter` are subclassable protocol
classes. A file tracer can map a measured filename to a logical source file;
the reporter supplies source text and a relative filename. Preserve the
method signatures and default behavior needed by plugins, including
`file_tracer`, `source_filename`, `line_number_range`, `source`, and
`relative_filename`.

### Command line

`python -m coverage run [options] FILE` executes a Python file while collecting
coverage and writes the selected data file. `python -m coverage report
[options]` reads that data and prints a deterministic table containing the
measured file names and totals. The installed `coverage` console script must
dispatch to the same implementation. Successful commands exit with status 0
and preserve the target program's stdout.

## Implementation Notes

- Keep the package split into focused modules: control, data/SQLite storage,
  reporting, parsing, configuration, plugin protocol, and CLI.
- The task's hidden verifier invokes the candidate through a UID-isolated JSON
  child process. Do not rely on importing candidate modules inside trusted
  verifier code, and do not write trusted result files from the candidate.
- The contract intentionally excludes native C tracer internals, multiprocessing
  coordination, sys.monitoring-specific details, TTY color output, and live
  external plugins. Implement the documented deterministic behavior faithfully
  and fail with the package's normal exceptions for invalid inputs.
- Generated reports must not include host-specific absolute paths in values
  that callers can reasonably compare; preserve the upstream format while
  keeping ordering stable.

## Examples

```python
from coverage import Coverage
cov = Coverage(data_file='.coverage')
with cov.collect():
    value = 1 + 1
cov.save()
```

```python
data = cov.get_data()
files = sorted(data.measured_files())
```

## Error Handling and Boundary Conditions

Missing or incompatible data files raise the package's coverage exceptions.
Report output must be deterministic and local; unsupported native tracers or
external plugins are outside this contract.
