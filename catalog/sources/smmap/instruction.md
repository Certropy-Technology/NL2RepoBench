# Project Description

`smmap` manages read-only memory-mapped views over local files. A manager
associates a path or an already-open file descriptor with regions, cursors
select which byte range is active, and `SlidingWindowMapBuffer` exposes a
relative byte/slice interface over a cursor. The implementation must use the
standard library `mmap` module and release mappings when their usage counts
reach zero.

This task is a bounded projection of the package's public behavior. It covers
local file mapping, region/window arithmetic, cursor lifecycle, sliding and
static managers, and the buffer interface. Packaged documentation, benchmark
throughput and platform-specific forced handle removal, while leaving
the remaining optional helpers are outside the contract.

## Natural Language Instruction

Create `smmap` from an empty workspace as a complete installable python project. Implement
the public operations, data or state behavior, input validation, deterministic ordering, and
error contracts documented below. Keep package metadata, root exports, module imports, and any
subpath entry points consistent across files. Implement the behavior rather than hard-coding the
examples, and do not retrieve or copy a reference implementation.

The finished repository must install from its root, expose every documented API family, preserve
the specified side effects and resource lifecycle, and remain usable in a fresh process.

## Supports

- Package/distribution name: `smmap`. Primary import or package entry: `smmap`.
- CPython 3.12.11 on debian-12-amd64 with pip.
- Install from `workspace/` using `python -m pip install .`.
- Declared dependency closure: setuptools==80.10.2, wheel==0.45.1. Standard-library modules are not dependencies.
- Build requirements are supplied before execution; do not add undeclared dependencies,
  registry overrides, download hooks, or source-fetch steps.
- Agent, candidate, verifier, Oracle, and controls use `network_mode=no-network`. Runtime access
  to GitHub, PyPI, npm, the Go proxy, DNS, and external services is forbidden.
- The declared test framework is `pytest`. A fixed collection
  contains `16` cases when that value is frozen in metadata;
  test implementation details are not part of the package surface.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── smmap/
│   ├── __init__.py
│   ├── util.py
│   ├── mman.py
│   └── buf.py
└── README.md
```

This is the required public project shape. Additional implementation modules are allowed only
when they support the documented API; evaluation, source-fetch, and private runtime files are
not agent-owned project files.

## API Usage Guide

### `smmap.util`

`align_to_mmap(num, round_up)` accepts a nonnegative integer byte offset/size
and returns the nearest multiple of `ALLOCATIONGRANULARITY`; it rounds down
when `round_up` is false and rounds up when true. `is_64_bit()` returns a bool.
`ALLOCATIONGRANULARITY` is the platform mmap allocation granularity and is a
positive integer.

`MapWindow(offset, size)` is a mutable window with integer `.ofs` and `.size`.
`ofs_end()` returns `ofs + size`. `MapWindow.from_region(region)` creates a
window covering the region. `align()` moves the beginning down to an mmap
boundary while preserving coverage and rounds the resulting size up.
`extend_left_to(window, max_size)` and `extend_right_to(window, max_size)`
expand toward an adjacent window without shrinking the existing window or
exceeding `max_size`; repeated calls after the limit are idempotent.

`MapRegion(path_or_fd, ofs, size, flags=0)` creates a read-only mapping. `ofs`
must be aligned to `ALLOCATIONGRANULARITY`, as required by the platform mmap
API; managers align larger windows before constructing regions. A string path
is opened and closed by the constructor; an integer FD remains owned by the
caller. The requested region is clamped to the available file bytes. It exposes
`buffer()`, `map()`, `ofs_begin()`, `size()`, `ofs_end()`,
`includes_ofs(ofs)`, `client_count()`, `increment_client_count(ofs=1)`, and
`release()`. The initial client count is one. A decrement to zero releases
the mapping and returns true; other count changes return false. `buffer()`
and `map()` expose the mapped read-only bytes.

`MapRegionList(path_or_fd)` is a list-compatible collection with
`path_or_fd()` and lazy `file_size()`. It preserves the exact path or FD value
and obtains size from `os.stat`/`os.fstat`.

### `smmap.mman`

`WindowCursor(manager=None, regions=None)` starts invalid. Its public methods
are `assign(rhs)`, `use_region(offset=0, size=0, flags=0)`,
`unuse_region()`, `buffer()`, `map()`, `is_valid()`, `is_associated()`,
`ofs_begin()`, `ofs_end()`, `size()`, `region()`, `includes_ofs(ofs)`,
`file_size()`, `path_or_fd()`, `path()`, and `fd()`. A manager-created cursor
is associated but invalid until `use_region` succeeds. `use_region` returns
the same cursor, maps from the requested absolute offset, clamps a zero size
to the available file/window size, and becomes invalid when `offset` is at or
past EOF. `buffer()` returns the active range as a memoryview. `path()` is
valid only for path-backed cursors; `fd()` is valid only for FD-backed cursors,
and the wrong query raises `ValueError`.

`StaticWindowMapManager(window_size=0, max_memory_size=0,
max_open_handles=sys.maxsize)` and
`SlidingWindowMapManager(window_size=-1, max_memory_size=0,
max_open_handles=sys.maxsize)` provide `make_cursor(path_or_fd)`, `collect()`,
`num_file_handles()`, `num_open_files()`, `window_size()`,
`mapped_memory_size()`, `max_file_handles()`, `max_mapped_memory_size()`,
and `force_map_handle_removal_win(base_path)`. Defaults choose positive
architecture-dependent limits. `make_cursor` returns an associated
`WindowCursor`; `collect()` releases unused regions and returns the number of
freed handles. The sliding manager may create multiple non-overlapping
windows, while the static manager may map the whole file in one region.

### `smmap.buf`

`SlidingWindowMapBuffer(cursor=None, offset=0, size=sys.maxsize, flags=0)`
creates a relative byte buffer. With a cursor it immediately calls
`begin_access`; with no cursor it is uninitialized, so call `end_access()` or
`begin_access()` before querying its length or indexing it.
`begin_access(cursor=None, offset=0, size=sys.maxsize, flags=0)` returns a
bool and reuses the current cursor when one is already associated. On success
`len(buffer)` is the requested size clamped to file size when the default
maximum is used. `buffer[index]` returns an integer byte and supports negative
indices; `buffer[start:stop]` returns bytes for ranges that cross windows and
supports negative bounds. Access requires a valid cursor. `end_access()` is
idempotent, resets the length to zero, and unuses the active region.
`cursor()` returns the current cursor. The object is also a context manager
that ends access on exit.

## Implementation Notes

Keep utility data types, manager/cursor state, and the relative buffer in
separate modules with the documented root re-exports. Preserve bytes exactly:
mapping a file must not decode or normalize its contents. File descriptors
passed by the caller must not be closed by `MapRegion`; path-backed mappings
must close only the constructor's temporary descriptor. Fresh manager and
buffer instances must produce the same bytes for the same file contents.
Handle empty and out-of-range accesses with ordinary Python behavior and
release all mappings before temporary files are removed. Do not copy an
upstream implementation or tests into the generated project.

Use the public language semantics described by each API family. Keep repeated calls deterministic
unless state mutation is explicitly part of the contract. Public re-exports and declarations must
match runtime behavior, and installation must not rely on a repository checkout or network access.

## Examples

The API-specific examples above are normative demonstrations of ordinary behavior. These four
local snippets also provide ordinary and boundary-oriented calls without external services:

```python
import smmap
print(smmap)
```

```python
import smmap
# Invoke a documented API using an empty or boundary input.
```

```python
import smmap
print(smmap)
```

```python
import smmap
# Invoke a documented API using an empty or boundary input.
```

## Error Handling and Boundary Conditions

Empty values, malformed values, unsupported types, exhausted inputs, invalid options, and missing
local resources must follow the API-specific contracts above. Preserve documented exception types
and messages where they are stated. Do not silently coerce an unsupported value merely to produce
a result, and do not mutate caller-owned data unless the relevant API explicitly promises it.

All filesystem, process, terminal, clock, randomness, and service interactions are forbidden unless
the API guide explicitly includes that local behavior. Even for an API that models remote or async
work, evaluation must remain bounded, deterministic, and disconnected from public networks.
