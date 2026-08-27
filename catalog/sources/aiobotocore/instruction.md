# Build `aiobotocore`

Create a complete, installable Python package named `aiobotocore` from an empty
workspace. It is an asyncio-friendly adaptation of botocore: local service
models and request machinery must work without AWS credentials, an AWS account,
or network access. Do not copy the upstream source or tests into the generated
workspace.

## Project Description

Implement a deterministic offline subset of aiobotocore 3.9.1 for CPython 3.12
on Linux. The package must expose async session/client construction around the
installed `botocore` models, async request/response helpers, configuration
merging, paginators, waiters, and a stubber that prevents real HTTP calls.
Live AWS calls, metadata services, credential-process commands, proxy/TLS
integration, CRT acceleration, and service-side behavior are out of scope.

## Supports

- Install from a source-only workspace with `pip install .` or the Harbor
  candidate installer; the build must also work without a `.git` directory.
- Python 3.12 on Linux amd64.
- Runtime dependencies are preinstalled by the environment: `aiohttp 3.14.3`,
  `aioitertools 0.13.0`, `botocore 1.43.75`, `jmespath 1.1.0`, `multidict
  6.7.1`, `python-dateutil 2.9.0.post0`, `six 1.17.0`, `urllib3 2.5.0`, and
  `wrapt 2.3.0`. Hatchling and hatch-fancy-pypi-readme are build backends.
- Runs are offline and deterministic. Never invoke `git`, `curl`, `wget`, an
  AWS endpoint, the metadata service, or a credential subprocess at runtime.

## API Usage Guide

### Package and session

`aiobotocore.__version__` must be the string `"3.9.1"`. Import
`aiobotocore.session.get_session()` to obtain a fresh `AioSession`; its
`user_agent_name` is `"aiobotocore"` and its version is `"3.9.1"`.

`AioSession.get_available_services()` returns a deterministic list containing
`"s3"` and `"dynamodb"`. `await AioSession.get_available_regions(service)`
returns a deterministic region list for a known service and raises the normal
botocore error for an unknown service. `get_service_model("s3")` returns a
botocore service model whose name is `"s3"` and which includes operations such
as `ListBuckets` and `PutObject`.

### Configuration

`AioConfig(**kwargs)` accepts botocore client settings such as
`region_name`, `connect_timeout`, `read_timeout`, `retries`,
`user_agent_extra`, and `connector_args`. `merge(other)` returns a new config,
does not mutate either input, and preserves options not specified by `other`.
Invalid connector arguments raise `botocore.exceptions.ParamValidationError`.

### Async clients, paginators, and waiters

`AioSession.create_client(service_name, region_name=...,` credentials and
`config=...)` returns an asynchronous context manager. Inside
`async with`, an S3 client exposes `meta.service_model.service_name`,
`meta.region_name`, `get_paginator("list_objects_v2")`, and the standard
`waiter_names` including `"bucket_exists"`. Paginator and waiter methods are
asynchronous and must not perform a request until called.

### Stubbed calls

`AioStubber(client)` supports `activate()`, `deactivate()`, and context-manager
use. `add_response(operation, response, expected_params=None)` queues a
response; `add_client_error(operation, error_code, error_message=None,
expected_params=None)` queues a typed client error. Queued calls are consumed
in order. An unexpected operation or parameter mismatch raises the appropriate
botocore stub exception, and an active stub must prevent any network request.

### Request and response helpers

`AioAWSResponse(url, status_code, headers, raw)` wraps an async raw response.
`AioStreamingBody(raw_stream, content_length)` supports `await read()`,
`await read(n)`, `tell()`, `readline()`, `readlines()`, async iteration, and
`close()`/`__aenter__`/`__aexit__` semantics. It must detect a short body and
raise the documented incomplete-read error.

## Implementation Notes

Keep public re-exports and exception identity consistent with botocore and
preserve insertion order in observable lists and dictionaries. Model data is
provided by the installed botocore dependency; do not download models. Async
methods must be awaitable and must clean up their HTTP session on context exit.
Use subprocess-safe, JSON-serializable behavior for ordinary values. Typed
errors are part of the contract; do not replace them with generic `Exception`.
