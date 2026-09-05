# Project Description

`s3fs` provides an fsspec-compatible filesystem interface over S3. It exposes
`S3FileSystem` for filesystem operations, `S3File` for buffered object access,
and `S3Map` for an fsspec mapping. The task focuses on the package contract,
path and option handling, deterministic filesystem/cache behavior, and the
object-call boundary using a small in-process fake client. Real S3 credentials
and network service behavior are outside this task.

## Natural Language Instruction

Create `s3fs` from an empty workspace as a complete installable python project. Implement
the public operations, data or state behavior, input validation, deterministic ordering, and
error contracts documented below. Keep package metadata, root exports, module imports, and any
subpath entry points consistent across files. Implement the behavior rather than hard-coding the
examples, and do not retrieve or copy a reference implementation.

The finished repository must install from its root, expose every documented API family, preserve
the specified side effects and resource lifecycle, and remain usable in a fresh process.

## Supports

- Package/distribution name: `s3fs`. Primary import or package entry: `s3fs`.
- CPython 3.12.11 on debian-12-amd64 with pip.
- Install from `workspace/` using `python -m pip install .`.
- Declared dependency closure: aiobotocore==2.25.1, aiohttp==3.12.15, fsspec==2026.7.0, pytest==9.1.1, setuptools==84.0.0, wheel==0.46.1. Standard-library modules are not dependencies.
- Build requirements are supplied before execution; do not add undeclared dependencies,
  registry overrides, download hooks, or source-fetch steps.
- Agent, candidate, verifier, Oracle, and controls use `network_mode=no-network`. Runtime access
  to GitHub, PyPI, npm, the Go proxy, DNS, and external services is forbidden.
- The declared test framework is `pytest`. A fixed collection
  contains `20` cases when that value is frozen in metadata;
  test implementation details are not part of the package surface.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── s3fs/
│   ├── __init__.py
│   ├── core.py
│   ├── mapping.py
│   ├── errors.py
│   └── utils.py
└── README.md
```

This is the required public project shape. Additional implementation modules are allowed only
when they support the documented API; evaluation, source-fetch, and private runtime files are
not agent-owned project files.

## API Usage Guide

### `s3fs.S3FileSystem`

Import path: `from s3fs import S3FileSystem`

Constructor signature:
`S3FileSystem(anon=False, endpoint_url=None, key=None, secret=None, token=None,
use_ssl=True, client_kwargs=None, requester_pays=False,
default_block_size=None, default_fill_cache=True, default_cache_type="readahead",
version_aware=False, config_kwargs=None, s3_additional_kwargs=None, session=None,
username=None, password=None, cache_regions=False, asynchronous=False, loop=None,
max_concurrency=10, fixed_upload_size=False, local_expiry_check=False, **kwargs)`.

Store the options on the instance and preserve these rules: `username` is an
alias for `key`, `password` is an alias for `secret`, supplying both spellings
raises `KeyError`, and `max_concurrency` must be at least one. The default
block size is 50 MiB, `protocol` contains `"s3"` and `"s3a"`, and
`requester_pays=True` adds `RequestPayer: requester` to S3 calls unless a
narrower call explicitly disables it.

`split_path(path) -> tuple[str, str, str | None]` accepts `s3://` and `s3a://`
paths as well as unprefixed paths. It returns `(bucket, key, version_id)`;
the key preserves a trailing slash, and a `?versionId=...` query is returned
only when `version_aware=True`. AWS access point and outposts ARNs are treated
as the bucket portion rather than split at their internal slashes.

`exists(path) -> bool`, `info(path, detail=True) -> dict`, and
`ls(path, detail=False, refresh=False, versions=False)` are synchronous
filesystem operations. The root exists without a client. Directory listings
are sorted by name and may be cached; `invalidate_cache(path=None)` clears the
whole listing cache or the requested path and its parent listings.

`open(path, mode="rb", **kwargs) -> S3File` supports `rb`, `wb`, `ab`, `r`,
`w`, and `a` forms. A key-like path is required. `open_async(path, mode="rb",
**kwargs)` is an async method and accepts only binary modes without
compression. `pipe_file(path, data, **kwargs)` uploads bytes through the S3
call boundary and `cat_file(path, start=None, end=None, **kwargs)` reads bytes.

### `s3fs.S3File`

Import path: `from s3fs import S3File`.

`S3File` is returned by `S3FileSystem.open` and follows buffered-file
semantics. For reads, `read`, `seek`, `tell`, `readline`, and iteration use
byte data and preserve range boundaries. For writes, `write` buffers bytes and
`close` commits a small object with one `put_object` call; `discard` abandons
an in-progress upload. `metadata`, `getxattr`, `setxattr`, and `url` delegate
to the owning filesystem.

### `s3fs.S3Map`

Import path: `from s3fs import S3Map`.

`S3Map(root, s3, check=False, create=False)` returns an fsspec `FSMap` rooted
at `root`. When `s3` is falsey it uses `S3FileSystem.current()`. Preserve the
mapping's root, key translation, and delegation to the supplied filesystem.

### Helpers and errors

Import paths `s3fs.core.calculate_chunksize`, `s3fs.core.version_id_kw`,
`s3fs.utils.title_case`, `s3fs.utils.SSEParams`, and
`s3fs.errors.translate_boto_error` are supported helper APIs. `calculate_chunksize`
uses a 50 MiB default and increases it only when the requested file would
exceed 10,000 parts. `version_id_kw(None)` and `version_id_kw("")` return an
empty dict; a nonempty version returns `{"VersionId": value}`. `title_case`
converts underscore-separated words to concatenated capitalized words.
`SSEParams.to_kwargs()` returns only configured server-side-encryption fields.
`translate_boto_error` maps
known S3 error codes to ordinary Python exceptions and preserves the original
exception as `__cause__` by default.

`add_retryable_error(exception_type)` extends the retryable exception types.
`set_custom_error_handler(callable)` installs the callable used by the retry
boundary; it must accept one exception and return a boolean.

## Implementation Notes

Use `fsspec.AsyncFileSystem` and `AbstractBufferedFile` rather than replacing
them with a parallel filesystem abstraction. Keep S3 API calls behind the
async `_call_s3` boundary so a fake async client can deterministically provide
`head_object`, `list_objects_v2`, `get_object`, and `put_object` responses.
registration of `s3` and `s3a`, requester-pays propagation, sorted listings,
cache invalidation, async stream reads, and normal exception types. Boundary
inputs, failed calls, and byte ranges are part of the required behavior in
addition to ordinary examples.

Use the public language semantics described by each API family. Keep repeated calls deterministic
unless state mutation is explicitly part of the contract. Public re-exports and declarations must
match runtime behavior, and installation must not rely on a repository checkout or network access.

## Examples

The API-specific examples above are normative demonstrations of ordinary behavior. These four
local snippets also provide ordinary and boundary-oriented calls without external services:

```python
import s3fs
print(s3fs)
```

```python
import s3fs
# Invoke a documented API using an empty or boundary input.
```

```python
import s3fs
print(s3fs)
```

```python
import s3fs
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
