# Build `gitdb`

Create an installable Python package named `gitdb` from an empty workspace.
This task covers a deterministic, local subset of GitDB 4.0.12: Git object
metadata and streams, in-memory object storage, loose-object storage, and the
Git-style object-database composition. The implementation must work without
network access and without a preinstalled copy of `gitdb`.

## Project Description

GitDB is a pure-Python library for reading and writing Git object data. Git
objects have a type, an uncompressed byte size, a binary SHA-1 identifier, and
content bytes. The supported databases use the standard Git loose-object
encoding: the SHA-1 is calculated from `b"<type> <size>\\0" + content`, while
the persisted loose-object file is a zlib-compressed form of those bytes.

The reference source revision is behavior evidence only. Do not copy reference
source files or upstream tests into the generated project. Implement the
observable contract here, including normal Python error behavior.

## Supports

- Support CPython `>=3.9,<4` and install from source using a normal PEP 517
  build configuration. A source tree without `.git` must install successfully.
- The runtime dependency is `smmap>=3.0.1,<6`, installed in the supplied base
  image during its build. Do not require the `git` command, a Git repository,
  native extensions, or a network connection at runtime.
- Keep all object, filesystem, compression, and stream operations local. Do
  not invoke subprocesses or access a service.
- Use `bytes` for object content and binary SHA values. A binary SHA is exactly
  20 bytes and its hexadecimal form is 40 lowercase ASCII characters/bytes.

## Natural Language Instruction

Create the installable `gitdb` package from an empty workspace. Reproduce all
public object records, streams, memory/loose/Git database operations, and error
contracts listed below, including deterministic byte and offset behavior.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
└── gitdb/
    ├── __init__.py
    ├── base.py
    ├── db.py
    ├── stream.py
    ├── loose.py
    └── exc.py
```

Use the exact submodule paths named in the API guide; package metadata must
install the `gitdb` import package. Private verifier files are excluded.

## Examples

```python
from gitdb.db import MemoryDB
db = MemoryDB(); stream = db.store(b'payload')
```

```python
from gitdb.stream import Sha1Writer
writer = Sha1Writer(); writer.write(b'abc'); writer.close()
```

## Error Handling and Boundary Conditions

Preserve missing-object, invalid-object, short-read, offset, empty-byte, and
closed-stream behavior. File-backed operations must stay within caller paths,
remain deterministic, and never use network access.

## API Usage Guide

### Package exports and constants

The root package must export these public names:

```text
OInfo, OPackInfo, ODeltaPackInfo, OStream, OPackStream, ODeltaPackStream,
IStream, InvalidOInfo, InvalidOStream, MemoryDB, LooseObjectDB, GitDB,
ObjectDBR, ObjectDBW, FileDBBase, CompoundDB, Sha1Writer,
ZippedStoreShaWriter, FlexibleSha1Writer, NullStream
```

Also provide `gitdb.__version__` as a nonempty string and package modules
`gitdb.base`, `gitdb.db.mem`, `gitdb.db.loose`, `gitdb.db.git`, `gitdb.fun`,
`gitdb.stream`, `gitdb.util`, and `gitdb.exc`. The root re-exports must have
the same object identity as their documented submodule definitions.

Use the type strings `b"commit"`, `b"tree"`, `b"blob"`, and `b"tag"`.
`gitdb.fun.type_to_type_id_map` maps those types to `1`, `2`, `3`, and `4`;
`type_id_to_type_map` provides the inverse for these ordinary types.

### Object records and streams

```python
OInfo(sha, type, size)
OPackInfo(packoffset, type_id, size)
ODeltaPackInfo(packoffset, type_id, size, delta_info)
OStream(sha, type, size, stream)
OPackStream(packoffset, type_id, size, stream)
ODeltaPackStream(packoffset, type_id, size, delta_info, stream)
IStream(type, size, stream, sha=None)
InvalidOInfo(sha, exc)
InvalidOStream(sha, exc)
```

`OInfo` is tuple-like and exposes `binsha`, `hexsha`, `type`, `type_id`, and
`size`. `OPackInfo` exposes `pack_offset`, `type`, `type_id`, and `size`.
`ODeltaPackInfo.delta_info` returns its fourth value. `OStream`,
`OPackStream`, and `ODeltaPackStream` provide `.stream` and `.read(size=-1)`
in addition to their corresponding information properties. Their `read`
method delegates to the supplied stream without changing its content.

`IStream` is mutable. It exposes read/write properties `binsha`, `type`,
`size`, `stream`, read-only `hexsha`, `.read(size=-1)`, and a writable
`.error`. Its supplied stream need only provide `.read`. Storing an `IStream`
sets its `binsha` to the computed binary digest and returns the same instance.

`InvalidOInfo` and `InvalidOStream` expose `binsha`, `hexsha`, and `error`.

### Stream writers and helpers

```python
Sha1Writer()
Sha1Writer.write(data)
Sha1Writer.sha(as_hex=False)
FlexibleSha1Writer(writer)
ZippedStoreShaWriter()
NullStream()

gitdb.fun.loose_object_header(type, size)
gitdb.fun.loose_object_header_info(buffer)
gitdb.fun.write_object(type, size, read, write, chunk_size=...)
gitdb.fun.stream_copy(read, write, size, chunk_size)
gitdb.util.bin_to_hex(binsha)
gitdb.util.hex_to_bin(hexsha)
```

`Sha1Writer.write(bytes)` updates a SHA-1 digest and returns the number of
input bytes. `.sha()` returns 20 digest bytes; `.sha(as_hex=True)` returns the
40-character lowercase hex string. `FlexibleSha1Writer` also forwards every
written byte string to its callback. `ZippedStoreShaWriter` tracks the digest,
zlib-compresses written bytes, requires `.close()` to flush, supports
`.seek(0)`, and returns compressed bytes through `.getvalue()`.

`loose_object_header(b"blob", 3)` returns `b"blob 3\\0"`.
`loose_object_header_info` accepts zlib-compressed loose-object bytes and
returns their `(type, size)` header tuple; malformed or incomplete input raises
a normal Python exception. `write_object`
writes the header followed by exactly `size` bytes obtained from `read`.
`stream_copy` copies at most `size` bytes in positive chunks and returns the
number copied. `bin_to_hex` and `hex_to_bin` round trip binary SHA values.

### `MemoryDB`

```python
MemoryDB()
MemoryDB.store(istream)
MemoryDB.has_object(sha)
MemoryDB.info(sha)
MemoryDB.stream(sha)
MemoryDB.size()
MemoryDB.sha_iter()
MemoryDB.stream_copy(sha_iter, odb)
```

`MemoryDB` stores immutable objects by computed binary SHA. `store` accepts an
`IStream`, consumes exactly its declared content, computes the Git object SHA,
and returns that same stream with `binsha` set. Storing identical type/content
is idempotent. `has_object` returns a boolean; `.size()` counts unique
objects; `.sha_iter()` yields every binary SHA once. `info(sha)` and
`stream(sha)` return information/stream records for the object; each fresh
`.stream(sha)` can be read from the beginning. A missing object raises
`gitdb.exc.BadObject`.

`stream_copy` copies only objects absent from a `LooseObjectDB` target and
returns the count it actually copied. `set_ostream` raises
`gitdb.exc.UnsupportedOperation` for `MemoryDB`.

### `LooseObjectDB`

```python
LooseObjectDB(root_path)
LooseObjectDB.object_path(hexsha)
LooseObjectDB.readable_db_object_path(hexsha)
LooseObjectDB.partial_to_complete_sha_hex(partial_hexsha)
LooseObjectDB.store(istream)
LooseObjectDB.has_object(sha)
LooseObjectDB.info(sha)
LooseObjectDB.stream(sha)
LooseObjectDB.sha_iter()
LooseObjectDB.size()
```

`root_path` is a local writable directory. For a 40-character hexadecimal SHA,
`object_path` returns the relative path `"aa/bb..."` formed from its first two
and remaining 38 characters, preserving bytes input as bytes output. `store` creates parent directories as necessary,
persists a zlib-compressed loose object at that path, and is idempotent for an
existing object. Stored object files must be readable after a fresh database
instance is constructed for the same root.

`readable_db_object_path` returns the complete local path for an existing
object and raises `BadObject` otherwise. `partial_to_complete_sha_hex` accepts
a bytes or text hexadecimal prefix and returns the unique matching binary SHA;
it raises `BadObject` for no match and `AmbiguousObjectName` for multiple
matches. `sha_iter` yields every stored binary SHA once; callers must not rely
on filesystem enumeration order. `info` and `stream` match `MemoryDB` semantics.

### `GitDB` composition

```python
GitDB(root_path)
```

`GitDB` operates on a Git objects directory. It requires that `root_path`
exist; loose objects live directly under it and packed objects are outside this
task. Its read, information, iteration, size, store, output-stream, and
partial-SHA operations delegate to its loose-object database. Creating it for
a missing root raises `gitdb.exc.InvalidDBRoot`.

### Errors and determinism

The following exception classes must be importable from `gitdb.exc`:

```text
BadObject, AmbiguousObjectName, UnsupportedOperation, InvalidDBRoot
```

They are normal exceptions; `BadObject` is raised on an unknown object and
`AmbiguousObjectName` on a non-unique prefix. Fixed inputs must yield the same
SHA, loose object bytes, metadata, and stream contents in fresh processes. Do
not promise filesystem enumeration order, file inode numbers, mtimes, or
private cache layout.

## Implementation Notes

Keep record/stream definitions, object-database interfaces, memory storage,
loose filesystem storage, and helper functions modular. A source-only build
may use `setuptools` or another PEP 517 backend, but it must have no runtime
third-party dependency beyond the declared `smmap` range. Pack parsing, delta resolution, alternates,
memory-mapped accelerators, reference databases, performance tests, and
long-lived file-handle behavior are outside this bounded contract.
