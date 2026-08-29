# Build `fsspec`

Create an installable Python project named `fsspec` from an empty workspace. The
project is a pure-Python filesystem abstraction library. Implement the package
layout and the public behavior below without copying an existing installed
`fsspec` or using network access during evaluation.

## Project Description

`fsspec` provides a common Python interface for filesystem implementations. The
base classes define filesystem operations, `MemoryFileSystem` supplies a fully
local in-memory backend, `FSMap` exposes a filesystem as a mutable byte mapping,
and the core helpers open files through protocol URLs. The package also includes
deterministic path utilities and byte-range caches.

## Supports

- Support CPython 3.10 and newer Python 3.x versions in the supported source
  range; the evaluation image uses CPython 3.12.
- Provide an installable top-level `fsspec` package with `fsspec.__all__`,
  `fsspec.__version__`, and the documented submodules.
- Declare no runtime third-party dependencies. Build requirements may be pinned
  separately, but the installed library must run with the standard library.
- Keep the evaluated behavior local and deterministic. The contract does not
  require credentials, cloud accounts, SSH, FUSE, databases, GUI libraries,
  subprocesses, or access to a live HTTP/FTP/S3/GCS service.
- Implement normal Python file-like and mapping protocols, preserve callback
  ordering where applicable, and raise ordinary documented exceptions rather
  than swallowing errors.

## API Usage Guide

### `fsspec.implementations.memory.MemoryFileSystem`

Import with `from fsspec.implementations.memory import MemoryFileSystem`.
`MemoryFileSystem(skip_instance_cache=True)` creates a local in-memory backend.
The backend stores bytes under normalized absolute paths. `pipe_file(path,
value)`, `open(path, mode)`, `cat_file(path, start=None, end=None)`, `info(path)`,
`ls(path, detail=True)`, `find(path, detail=False)`, `glob(pattern)`, `exists`,
`isfile`, `isdir`, `mkdir`/`makedirs`, `copy`, `mv`, and `rm` must provide the
usual filesystem behavior. Directory entries have `type="directory"` and
files have `type="file"`; file info includes `name` and byte `size`.

Paths may be written as `memory:///name` or `/name` and must normalize to the
same backend path. Listing and `find` results are sorted where the API returns
names. Missing paths raise `FileNotFoundError`; opening a directory raises
`IsADirectoryError`; attempting to create an existing path raises
`FileExistsError`.

`MemoryFileSystem.store` is shared by instances as in the upstream in-memory
backend. Tests should clear it before an independent scenario. `MemoryFile`
objects are byte streams with `read`, `write`, `seek`, `tell`, `size`, context
manager support, and commit semantics compatible with the filesystem.

### Base filesystem and mappings

`fsspec.spec.AbstractFileSystem` supplies common operations such as `walk`,
`find`, `glob`, `du`, `cat`, `pipe`, `read_bytes`, `write_bytes`, `head`,
`tail`, `expand_path`, and `get_mapper`. Implementations may override backend
operations but should retain the base method contracts.

`fsspec.mapping.FSMap(root, fs, check=False, create=False)` is a
`collections.abc.MutableMapping` whose keys are relative paths below `root`
and whose values are bytes. `__getitem__`, assignment, deletion, iteration,
`len`, `getitems`, `setitems`, `delitems`, `clear`, `pop`, and membership must
map to the filesystem. Missing keys raise `KeyError`; non-byte values are
accepted only when the backend's documented byte conversion supports them.
`fsspec.mapping.get_mapper(url, ...)` creates an `FSMap` after resolving the
URL.

### Core opening and URL helpers

`fsspec.core.url_to_fs(url, **kwargs)` returns `(filesystem, path)` after
resolving a protocol and stripping its URL prefix. `fsspec.open(urlpath,
mode="rb", compression=None, encoding="utf8", errors=None, protocol=None,
newline=None, expand=None, **kwargs)` returns an `OpenFile`. Entering an
`OpenFile` opens the backend file, optionally wraps a standard compression codec,
and optionally returns a text stream. It must close all wrapped streams on exit.
`open_files(...)` returns an `OpenFiles` list/context manager and supports an
explicit list of paths or deterministic wildcard expansion for local paths.

`split_protocol(url)` returns `(protocol, path)` or `(None, url)` for an
unqualified local path. `strip_protocol(url)` returns the backend path.
`get_compression(path, compression)` accepts a registered codec name, `None`,
or `"infer"`, and rejects unknown codecs with `ValueError`.

### Utilities and caches

Implement the public functions in `fsspec.utils` used by ordinary local code,
including `infer_storage_options`, `update_storage_options`,
`infer_compression`, `build_name_function`, `seek_delimiter`, `read_block`,
`tokenize`, `stringify_path`, `common_prefix`, `other_paths`, `is_exception`,
`isfilelike`, `get_protocol`, `get_file_extension`, `can_be_local`,
`merge_offset_ranges`, `file_size`, and `glob_translate`. They must preserve
input ordering and stable formatting. `tokenize` returns a deterministic
32-character hexadecimal token for equal inputs.

`fsspec.caching.AllBytes`, `ReadAheadCache`, and `BlockCache` implement the
`BaseCache(blocksize, fetcher, size)` contract. `fetcher(start, end)` returns
bytes for a half-open range. `_fetch(start, end)` returns the requested bytes,
reuses cached data where possible, and updates the cache's observable state.
Repeated reads must not corrupt or reorder bytes; pickling support must retain
the documented cache state where the class provides it.

The registry must expose `filesystem`, `get_filesystem_class`,
`register_implementation`, `available_protocols`, and the built-in `file`,
`local`, and `memory` implementations. `fsspec.__all__` should re-export the
same canonical objects rather than duplicate incompatible classes.

## Implementation Notes

Use a `src/`-independent or `src/fsspec/` package layout that works with a
standard PEP 517 build. The candidate installation is performed before hidden
tests and the hidden tests are not present in the candidate workspace. Do not
hard-code hidden expected outputs or write verifier reports from candidate code.

Normal library operations must not fetch anything, inspect the reference
checkout, or depend on the test bundle. Preserve protocol normalization,
filesystem instance caching behavior, byte ranges, sorted path results, and
standard exception types. Optional backends may be present as importable
modules only when their imports fail gracefully without optional dependencies;
the scored contract is the local, dependency-free surface described above.
