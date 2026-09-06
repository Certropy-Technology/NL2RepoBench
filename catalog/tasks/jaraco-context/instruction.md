# Project Description

Build the installable Python package `jaraco.context` from an empty workspace.
It provides context managers for temporary directories, working-directory
changes, safe tar extraction, repository command setup, exception trapping,
suppression, and interrupt policy. The package must be usable on Python 3.12
Linux with deterministic local behavior.

# Natural Language Instruction

Implement the public `jaraco.context` context-manager and helper contract. A
caller must be able to push and restore directories, create and clean temporary
directories, compose context managers, strip an archive root safely, and use
exception/decorator helpers. Keep tar extraction traversal-safe and preserve
cleanup on normal and exceptional exits. The package is a library, not a
network service; do not add tests, verifier files, or reference source to the
generated workspace.

# Supports or Environment Configuration

- Python 3.12 on Linux; distribution and import package are both
  `jaraco.context`.
- Provide a root `pyproject.toml` and installable PEP 517 package with version
  `6.1.3.dev6+gbfcb95c78`.
- Build-only dependencies stay out of runtime dependencies. Runtime execution
  must not access a network service or external data.
- `tarball` and `repo_context` describe APIs that accept URL/command inputs,
  but evaluation observes them through bounded local adapters; never contact a
  network during agent, candidate, verifier, Oracle, or control runs.

# Project Directory Structure

```text
workspace/
├── pyproject.toml
├── README.md
├── LICENSE
└── jaraco/
    ├── __init__.py
    └── context/
        ├── __init__.py
        └── py.typed
```

# API Usage Guide

```python
pushd(dir)
temp_dir(remover=shutil.rmtree)
robust_remover()
robust_temp_dir
tarball(url, target_dir=None)
tarball_cwd(url, target_dir=None)
strip_first_component(member, path)
_default_filter(member, path)
_compose_tarfile_filters(*filters)
_compose(*context_managers)
repo_context(url, branch=None, quiet=True, dest_ctx=robust_temp_dir)
```

`pushd` changes to `dir`, yields it, and restores the previous directory even
when the body raises. `temp_dir` yields a temporary path and calls its remover
after exit; `robust_temp_dir` uses the platform remover. `strip_first_component`
mutates and returns the same `TarInfo`, removing its first slash-separated path
component. The default archive filter combines that operation with the standard
safe data filter. `_compose_tarfile_filters` applies filters left to right.

`tarball` streams a tar archive, strips its common root, yields the extraction
directory, and removes it afterward. Omitted `target_dir` derives from the URL
basename after removing `.tar.gz` or `.tgz`. Members escaping the destination
must be rejected. `tarball_cwd` composes extraction with `pushd`.

`_compose(*context_managers)` composes dependent factories from right to left:
the rightmost receives caller arguments and each factory to its left receives
the previously yielded value. `repo_context` creates a temporary destination,
selects `git clone` for URLs containing `git` and otherwise `hg clone`, adds an
optional branch, yields the destination, and cleans it through `dest_ctx`.
`quiet=True` routes clone output to `subprocess.DEVNULL`.

`ExceptionTrap(exceptions=(Exception,))` suppresses matching subclasses and
records `type`, `value`, and `tb`; its truth value is true after a match.
`.raises` and `.passes` are decorators that preserve wrapped metadata. A
nonmatching exception propagates. `suppress(*exceptions)` follows
`contextlib.suppress` and also decorates functions. `on_interrupt(action="error",
/, code=1)` propagates for `ignore`, suppresses for `suppress`, and raises
`SystemExit(code)` for `error`; other exception types propagate.

# Implementation Notes

Use context-manager protocols and `tarfile` safe filtering. Cleanup must run on
both success and failure, and `ExceptionTrap` must not retain a live traceback
after the context exits. Keep signatures and exception semantics stable. The
package must import in isolated Python mode from its installed target.

# Examples

```python
import os
from jaraco.context import pushd, temp_dir

original = os.getcwd()
with temp_dir() as path:
    with pushd(path):
        assert os.getcwd() == path
assert os.getcwd() == original
```

```python
from jaraco.context import ExceptionTrap, suppress

with ExceptionTrap((ValueError,)) as trap:
    raise ValueError("bad input")
assert trap and trap.type is ValueError

@suppress(KeyError)
def lookup(mapping):
    return mapping["missing"]
```

# Error Handling and Boundary Conditions

The task id is `jaraco-context`; the distribution is `jaraco.context`.

- Archive members with `..` or an absolute path that escapes the destination
  must fail rather than write outside the extraction directory.
- `pushd`, `tarball`, and temporary contexts restore/clean up when their body
  raises.
- `ExceptionTrap` suppresses only configured exception subclasses; unrelated
  exceptions propagate.
- `on_interrupt` accepts the documented actions only; the interrupt policy
  must not swallow unrelated exceptions.
- Runtime runs are no-network and must not invoke an external clone or download
  during verification.
