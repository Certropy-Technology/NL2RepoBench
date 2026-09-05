# Project Description

Create an installable Python package named `pathspec` that matches file paths
using Git-style wildcard rules. It must be a real package with a PEP 517 build,
the package layout and public behavior described below, and no network or
external-service behavior during import or normal use.

## Natural Language Instruction

Create the installable `pathspec` project from an empty `workspace/`. Implement
the root exports, pattern compilation, Git wildmatch and Git ignore precedence,
path matching, deterministic filesystem traversal, registration helpers, and
the documented data classes. Keep matching local and deterministic; optional
native backends and external services are outside the required project.

# Supports

- Support CPython 3.9 and newer, with the evaluation runtime using Python 3.12.
- Use a standard installable `pyproject.toml` and expose `pathspec/__init__.py`.
- Provide `pathspec/py.typed` and keep runtime dependencies empty.
- Preserve the package version `1.1.1` and the root exports listed below.
- Implement the always-available `simple` matching backend. Optional native
  `re2` and `hyperscan` backends are outside this task and must not be required.
- Do not clone, download, invoke a package manager, or contact a service during
evaluation. Candidate dependencies are available only from the build image.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
└── pathspec/
    ├── __init__.py
    ├── pattern.py
    ├── patterns/
    │   ├── __init__.py
    │   └── gitwildmatch.py
    ├── util.py
    ├── spec.py
    └── py.typed
```

The package root re-exports the names documented below. `pathspec.pattern` and
`pathspec.patterns.gitwildmatch` provide the corresponding compiled pattern
classes, while `pathspec.util` contains filesystem and registration helpers.

# API Usage Guide

## Root exports

The package root must export `GitIgnoreSpec`, `PathSpec`, `Pattern`,
`RegexPattern`, `RecursionError`, and `lookup_pattern`, plus the metadata values
`__author__`, `__copyright__`, `__credits__`, `__license__`, and `__version__`.
`pathspec.__version__` must be the string `"1.1.1"`. Importing `pathspec`
must register the built-in `gitwildmatch` pattern factory.

## `Pattern` and `RegexPattern`

Import them from `pathspec.pattern`. `Pattern(include)` stores `include`, where
`True` means a matching rule selects a path, `False` means it removes a path,
and `None` is a no-op. `Pattern.match_file(file)` raises `NotImplementedError`
unless overridden. `Pattern.match(files)` yields each string whose
`match_file` result is non-`None`.

`RegexPattern(pattern, include=None)` accepts a string, bytes, compiled regular
expression, or `None`. String and bytes patterns are converted by
`pattern_to_regex`; a precompiled expression uses the supplied `include` value.
Its `match_file(file)` returns a `RegexMatchResult` for a search match and
`None` otherwise. Preserve `pattern`, `regex`, `include`, equality, `repr`, and
`str` behavior. `RegexPattern.pattern_to_regex(pattern)` returns `(pattern,
True)` by default.

## `GitWildMatchPattern`

Import it from `pathspec.patterns.gitwildmatch`. Its constructor compiles Git
wildmatch text. `pattern_to_regex(pattern)` returns `(regex, include)` and
supports comments beginning with `#`, a leading `!` exclusion, escaped special
characters, `*`, `?`, character classes, path separators, and `**`. A trailing
`/` is a directory marker and matching a directory also matches descendants.
Invalid input raises the documented `TypeError` or
`GitWildMatchPatternError`. `escape(value)` returns a same-type string/bytes
with Git metacharacters escaped. Preserve `_BYTES_ENCODING = "latin1"` and
`_DIR_MARK = "ps_d"`.

## `PathSpec`

Import `PathSpec` from `pathspec`. Construct it as
`PathSpec(patterns, *, backend=None)`, where `patterns` is a sequence or
iterable of compiled `Pattern` objects. `len(spec)`, equality, `repr`, `+`,
and `+=` operate on the compiled patterns. `backend="simple"` is always
available; the default may select the best available backend.

`PathSpec.from_lines(pattern_factory, lines, *, backend=None)` accepts a
registered factory name, a `Pattern` class, or a callable. It skips empty
lines, rejects non-iterable inputs with `TypeError`, and returns a new spec.
`match_file(file, separators=None)` returns a boolean. `check_file` returns a
`CheckResult(file, include, index)`, retaining the original input and the last
matching pattern index. `match_files` and `check_files` preserve input order;
their `negate=True` option inverts selection. `match_entries` and
`match_tree_entries` operate on `TreeEntry` objects. `match_tree_files` walks a
root and returns matching relative file paths. The deprecated `match_tree`
alias remains callable.

## `GitIgnoreSpec`

`GitIgnoreSpec` subclasses `PathSpec` and uses `GitWildMatchSpecPattern`
semantics. `GitIgnoreSpec.from_lines(lines, pattern_factory=None, *,
backend=None)` must also accept the historical reversed form
`from_lines(pattern_factory, lines)`. A later rule takes precedence, and
directory rules preserve Git's ability to include descendants. A basic
`GitIgnoreBasicPattern` factory must be rejected because it has different
semantics.

## Utilities and data classes

Import utilities from `pathspec.util`: `append_dir_sep`, `check_match_file`,
`detailed_match_files`, `iter_tree_entries`, `iter_tree_files`, `lookup_pattern`,
`match_file`, `match_files`, `normalize_file`, `register_pattern`,
`CheckResult`, `MatchDetail`, `TreeEntry`, `AlreadyRegisteredError`, and
`RecursionError`. Normalize path separators to `/` and remove one leading `/`
or `./` by default. Explicit `separators=()` disables replacement.

`iter_tree_files(root, on_error=None, follow_links=None, subdir=None)` yields
relative file paths. `iter_tree_entries` yields files and directories with
cached `stat` results. The default follows directory links and detects ancestor
recursion using `RecursionError`; `follow_links=False` yields links without
following them. A `subdir` must remain within `root`, otherwise raise
`ValueError`. File-system errors are ignored by default or passed to `on_error`.

`CheckResult` is a frozen data class with `file`, `include`, and `index`.
`TreeEntry` provides `name`, `path`, `is_dir`, `is_file`, `is_symlink`, and
`stat`. `RecursionError` exposes `real_path`, `first_path`, `second_path`, and
`message`. `register_pattern` rejects non-string names, non-callables, and
duplicate names unless `override=True`.

# Implementation Notes

Keep the candidate boundary installable from an empty directory and keep all
candidate code under its own package. The verifier checks behavior through a
UID-separated child process, so do not rely on importing a trusted reference
implementation or on files outside the candidate installation. Filesystem
examples in the API must be deterministic and local. Preserve iterator laziness
where the API returns an iterator, last-rule-wins matching, original path
objects in result iterators, and normal Python exceptions rather than silently
coercing invalid inputs.

## Examples

```python
from pathspec import GitIgnoreSpec, PathSpec

spec = PathSpec.from_lines('gitwildmatch', ['*.pyc', '!keep.py'])
spec.match_file('build.pyc')  # True
```

```python
from pathspec import GitIgnoreSpec

ignore = GitIgnoreSpec.from_lines(['build/', '!build/keep.txt'])
ignore.match_file('build/tmp.o')  # True
ignore.match_file('build/keep.txt')  # False
```

```python
from pathspec.util import normalize_file, register_pattern

normalize_file('./src\\main.py')  # 'src/main.py'
register_pattern('local', lambda value: None, override=True)
```

## Error Handling and Boundary Conditions

- Invalid wildmatch syntax and unsupported pattern inputs raise the documented
  `TypeError` or `GitWildMatchPatternError`; they are not silently treated as
  literal matches.
- `check_file` preserves the original path and reports the last matching rule;
  matching methods preserve input order and lazy iterator behavior.
- Filesystem traversal remains within the requested root. A subdirectory that
  escapes that root raises `ValueError`, and ancestor cycles raise the public
  `RecursionError` with its path metadata.
