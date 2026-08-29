# Build `s3fs`

Create an installable Python package named `s3fs` from an empty workspace. The
implementation must reproduce the behavior of the pinned `s3fs` release at
the API boundary described below. Evaluation is local and deterministic: do
not fetch source, install packages, contact AWS, or contact any other service
while the implementation is being evaluated.

## Project Description

`s3fs` provides an fsspec-compatible filesystem interface over S3. It exposes
`S3FileSystem` for filesystem operations, `S3File` for buffered object access,
and `S3Map` for an fsspec mapping. The task focuses on the package contract,
path and option handling, deterministic filesystem/cache behavior, and the
object-call boundary using a small in-process fake client. Real S3 credentials
and network service behavior are outside this task.

## Supports

- Support CPython 3.10 and newer, with the package metadata version matching
  the pinned upstream revision's `s3fs` distribution.
- Provide an installable package using `pip install .` and editable install.
- Declare the runtime dependencies `aiobotocore`, `fsspec`, and `aiohttp` with
  compatible version ranges. Do not vendor dependencies.
- Export `S3FileSystem`, `S3File`, `S3Map`, `add_retryable_error`, and
  `set_custom_error_handler` from `s3fs`.
- Keep operations deterministic and preserve the synchronous wrappers and
  asynchronous methods described here. Do not add a CLI or network fallback.

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
Candidate code must not import hidden tests or write trusted reports. Preserve
registration of `s3` and `s3a`, requester-pays propagation, sorted listings,
cache invalidation, async stream reads, and normal exception types. The hidden
suite intentionally checks boundary inputs, failed calls, and byte ranges in
addition to ordinary examples.
