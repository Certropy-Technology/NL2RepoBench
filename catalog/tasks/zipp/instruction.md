# Build `zipp`

Create a complete, installable Python distribution named `zipp` from an empty
workspace. The package is the portable implementation and upstream proving
ground for the standard library's `zipfile.Path`: it exposes pathlib-like
navigation over members of a ZIP archive without extracting the archive.

## Project Description

The import package is `zipp`. Implement the ZIP-backed path API, implicit
directory support, glob translation, compatibility overlay, and package
metadata described below. The evaluation runtime is CPython 3.12 on Linux.
Normal package use is local and deterministic: it must not contact a network,
launch a subprocess, or require an external service.

The distribution version is `4.1.0`. The distribution declares no third-party
runtime dependencies. Include an MIT `LICENSE` file so an offline PEP 517 build
does not need to retrieve license text.

## Supports

- Support CPython 3.10 and newer.
- Provide a normal PEP 517 `pyproject.toml` at the repository root and an
  installable `zipp` package.
- Export only `Path` through `zipp.__all__`, in that order.
- Keep `zipp.Path`, `zipp.CompleteDirs`, and `zipp.FastLookup` importable.
- Keep `zipp.glob` and `zipp.compat.overlay` importable. The overlay module
  exposes a hashable module-like `zipfile` object whose `Path` is `zipp.Path`
  and whose `_path` attribute is the `zipp` module.
- Preserve archive member order when iterating and globbing.
- Treat archive names as POSIX paths. A backslash in a member name is an
  ordinary character, not a separator.
- Do not extract members as part of normal navigation or reads.

## API Usage Guide

### `zipp.Path`

Import path and constructor:

```python
Path(root, at="")
```

`root` is either a filesystem path accepted by `zipfile.ZipFile` or an open
`zipfile.ZipFile`. `at` is the member name represented by the object and uses
forward slashes. Constructing from an existing ZIP object may specialize that
object in place to provide fast lookup and implicit directories. The public
attributes `root` and `at` remain inspectable.

```python
import io
import zipfile
from zipp import Path

data = io.BytesIO()
archive = zipfile.ZipFile(data, "w")
archive.writestr("docs/guide.txt", "hello")
archive.filename = "manual.zip"

root = Path(archive)
guide = root / "docs" / "guide.txt"
assert guide.read_text(encoding="utf-8") == "hello"
```

Path composition and navigation:

```python
path.joinpath(*other) -> Path
path / component -> Path
path.iterdir() -> iterator[Path]
path.parent -> Path | pathlib.Path
path.relative_to(other, *extra) -> str
```

`joinpath` accepts one or more string or path-like components. A directory
present only because child members exist resolves with a trailing slash.
`iterdir()` yields direct children in archive order, including implied
directories, and raises `NotADirectoryError` when called on a file. Child paths
preserve subclasses of `Path`. At the archive root, `parent` is the filesystem
parent of the ZIP filename; below the root it is another ZIP path. A missing
directory name with a trailing slash still has the expected ZIP parent.

Path state and metadata:

```python
path.name -> str
path.suffix -> str
path.suffixes -> list[str]
path.stem -> str
path.filename -> pathlib.Path
path.is_dir() -> bool
path.is_file() -> bool
path.exists() -> bool
path.is_symlink() -> bool
```

The archive root is a directory. A member ending in `/` is a directory.
`exists()` and `is_file()` consult the current archive state, so paths created
from a writable archive reflect members added later. `is_symlink()` interprets
the Unix mode stored in the member's external attributes. The filename,
suffix, and stem properties follow `pathlib` behavior for the final component.
At the root they describe the ZIP filename. If an in-memory ZIP has
`filename is None`, string conversion uses `:zipfile:`; root `name`,
`filename`, and `parent` raise `TypeError`, while those properties still work
for child members.

Reading and writing:

```python
path.open(mode="r", *args, pwd=None, **kwargs)
path.read_text(*args, **kwargs) -> str
path.read_bytes() -> bytes
```

Text opens use `io.TextIOWrapper` semantics, including positional or keyword
encoding and the usual `errors` handling. Binary opens reject text-only
arguments with `ValueError`. Opening a directory raises `IsADirectoryError`;
opening a missing member for reading raises `FileNotFoundError`. When the
underlying ZIP is writable, `open("w")` and `open("wb")` write text and bytes.
Closing a member stream must not close an externally supplied archive.

Matching:

```python
path.match(path_pattern) -> bool
path.glob(pattern) -> iterator[Path]
path.rglob(pattern) -> iterator[Path]
```

`glob` matches from the current ZIP path and preserves archive order. `*` and
`?` do not cross `/`; bracket character sets work; `**` is recursive only when
it occupies a complete path segment. Directory names may match without a
trailing slash. An empty pattern raises `ValueError`, as does a pattern that
embeds `**` inside another segment. `rglob(pattern)` is equivalent to recursive
`**/pattern` matching.

Two paths compare equal only when they have the same concrete class, archive
object, and member name. Equal paths have equal hashes. `repr(path)` includes
the concrete class name, archive filename, and member name. Paths backed by an
on-disk archive are pickleable; unpickling restores traversable behavior.

### `zipp.CompleteDirs`

`CompleteDirs` is a `zipfile.ZipFile` subclass that adds directory entries
implied by child names.

```python
CompleteDirs.make(source) -> CompleteDirs
CompleteDirs.inject(zf: zipfile.ZipFile) -> zipfile.ZipFile
complete.namelist() -> list[str]
complete.resolve_dir(name: str) -> str
complete.getinfo(name: str) -> zipfile.ZipInfo
```

`make` accepts a filename or existing ZIP object and returns an appropriate
specialized object. `namelist` appends missing parent directories in stable
first-seen order. `resolve_dir("pkg")` returns `"pkg/"` when only that
directory exists. `getinfo` returns a synthetic `ZipInfo` for an implied
directory but preserves `KeyError` for missing members. `inject` writes each
missing implied directory into a writable archive and returns that same
archive.

`FastLookup` is the read-only specialization used by `Path`; it caches the
complete name list and membership set. Writable archives must remain live and
must not use stale cached lookup data.

## Implementation Notes

- Malformed leading-slash names are not root children. Dot segments and names
  containing `:`, `?`, or backslashes remain addressable according to ZIP name
  rules; do not apply host-filesystem sanitization to member names.
- Preserve the external archive's lifetime and mutation behavior. Do not copy
  every archive into a new buffer merely to navigate it.
- Keep lookup and glob operations bounded and avoid repeatedly rebuilding the
  complete member set for an unchanged read-only archive.
- Hidden verification constructs ZIP fixtures only inside an unprivileged
  child process. The trusted verifier never imports candidate code and observes
  only bounded JSON results.
- Do not retrieve the upstream repository, its tests, or another installed
  `zipp` implementation at build or runtime.
