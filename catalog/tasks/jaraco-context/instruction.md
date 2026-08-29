# Project Description

Build an installable Python package named `jaraco.context` from an empty
workspace. The import package is `jaraco.context`. Implement the public runtime
behavior described below; the goal is compatibility with CPython 3.12 on Linux,
not static type-checker compatibility or documentation tooling.

# Supports

- Python 3.12 on Linux.
- A PEP 517 `pyproject.toml` at the repository root and an installable package.
- Distribution metadata for `jaraco.context` with version `6.1.3.dev6+gbfcb95c78`.
- No runtime network access and no runtime service or external data.
- The build backend may use the standard setuptools-based configuration. Keep
  build-only dependencies out of the installed package's runtime dependencies.

# API Usage Guide

Implement these importable names in `jaraco.context`:

`pushd(dir)` is a context manager that changes the current working directory,
yields the supplied path, and restores the previous directory even when the
body raises.

`temp_dir(remover=shutil.rmtree)` creates a temporary directory, yields its
path as a string, and invokes the supplied remover after the context exits.
`robust_remover()` returns the platform-appropriate recursive remover and
`robust_temp_dir` is the corresponding partial context manager.

`tarball(url, target_dir=None)` downloads a tar archive with
`urllib.request.urlopen`, streams its extraction, strips the common first path
component from members, yields the extraction directory, and removes that
directory on exit. When `target_dir` is omitted, derive it from the URL basename
by removing `.tar.gz` or `.tgz`. Extraction must reject archive members that
escape the destination. `tarball_cwd` composes `tarball` with `pushd` so the
current directory is the extracted directory while the body runs.

`strip_first_component(member, path)` removes the first slash-separated path
component from a `tarfile.TarInfo` and returns that same member. The module's
`_default_filter` combines this operation with the standard library's safe data
filter. `_compose_tarfile_filters` composes filters from left to right as used
by `_default_filter`.

`_compose(*context_managers)` composes dependent context-manager factories from
the innermost factory on the right to the outermost on the left. The rightmost
factory receives the caller arguments; each factory to its left receives the
previous yielded value.

`repo_context(url, branch=None, quiet=True, dest_ctx=robust_temp_dir)` creates a
temporary destination, runs `git clone` for URLs containing `git` (otherwise
`hg clone`), optionally adds `--branch BRANCH`, yields the destination, and
cleans it up through `dest_ctx`. When `quiet` is true, clone output is sent to
`subprocess.DEVNULL`.

`ExceptionTrap(exceptions=(Exception,))` is a context manager. It suppresses
matching exception subclasses and records `.type`, `.value`, and `.tb`; it does
not suppress nonmatching exceptions. Its truth value is true only after a
matching exception. `.raises` wraps a function and returns whether the selected
exceptions were raised; `.passes` returns whether the wrapped function completed
without a selected exception. Preserve wrapped function metadata.

`suppress(*exceptions)` behaves like `contextlib.suppress` and also works as a
decorator. `on_interrupt(action="error", /, code=1)` handles `KeyboardInterrupt`:
`"ignore"` propagates it, `"suppress"` suppresses it, and `"error"` raises
`SystemExit(code)` from the interrupt. Other exception types propagate.

# Implementation Notes

Preserve deterministic exception types/messages and context cleanup. Use
standard-library `tarfile` safe filtering on Python 3.12. Do not implement
`repo_context` by contacting the network during verification; the behavior is
observed through a bounded child-side adapter. Do not add test fixtures,
reference source, or verifier files to the candidate workspace. The package
must remain usable when imported with `python -I` from its installed target.
