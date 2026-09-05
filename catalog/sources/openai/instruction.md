# Build the offline OpenAI Python SDK core

Create a complete, installable Python package named `openai` from an empty
workspace. Implement the deterministic offline core contract below for CPython
3.12 on Linux amd64. Do not copy the upstream repository or its tests. The
package must build with `pip install .` from a source-only workspace and must
not require network access at runtime.

# Natural Language Instruction

Build the complete offline `openai` Python SDK core from an empty workspace.
Implement models, query serialization, incremental SSE decoding, webhook
verification, and injected sync/async HTTP clients exactly as specified below.
Create the package and build metadata rather than a single module, and keep the
generated endpoint and live service surface outside the task.

## Project Description

Recreate the stable core behavior of `openai` version `3.3.1`: Pydantic-backed
models, query-string serialization, incremental Server-Sent Events decoding,
webhook signature verification, and synchronous/asynchronous client request
construction. This task is an offline SDK exercise. It does not contact the
OpenAI service, read credentials from a network, or implement the generated
endpoint surface.

## Supports or Environment Configuration

- Python 3.12 on Linux amd64; use a `src/openai/` package layout and a
  `pyproject.toml` using the Hatchling build backend.
- Runtime dependencies are already installed: `anyio`, `httpx2`, `pydantic`,
  `typing-extensions`, `sniffio`, and `jiter`. Do not install packages at
  evaluation time and do not vendor dependencies.
- All ordinary values crossing an application boundary must remain JSON-safe.
  HTTP behavior is tested only with an injected `httpx2` transport; never call
  a real endpoint.
- Preserve insertion order in dictionaries and query parameters. Public
  exceptions must be typed and importable from their documented paths.

## Project Directory Structure

```text
workspace/
├── pyproject.toml          # Hatchling build metadata and dependencies
└── src/openai/
    ├── __init__.py         # root exports, version, sentinels
    ├── _models.py          # BaseModel and recursive construction
    ├── _qs.py              # query encoding and parsing
    ├── _streaming.py       # SSE event and decoder
    ├── lib/_webhooks.py    # signature verification and unwrap
    └── _client.py          # sync and async injected clients
```

The `src` mapping and public import paths must work after installation. No
endpoint fixture, private verifier, Oracle payload, or live-service code belongs
in the agent-owned tree.

## API Usage Guide

### Package exports and sentinels

`openai.__version__` is the string `"3.3.1"`. Re-export `OpenAI`,
`AsyncOpenAI`, `BaseModel`, `NOT_GIVEN`, `not_given`, `Omit`, `omit`,
`OpenAIError`, and `InvalidWebhookSignatureError` from `openai`.

`NotGiven` and `Omit` instances are falsey. Their representations are
`"NOT_GIVEN"` and a stable non-secret representation respectively. `NOT_GIVEN`
and `not_given` are distinct instances of the same sentinel type.

### Models

`openai.BaseModel` subclasses Pydantic's model and allows unknown fields.
Implement `to_dict(*, mode="python"|"json", use_api_names=True,
exclude_unset=True, exclude_defaults=False, exclude_none=False, warnings=True)`
and `to_json(*, indent=2|None, use_api_names=True, exclude_unset=True,
exclude_defaults=False, exclude_none=False, warnings=True)`. Nested models,
aliases, lists, dictionaries, datetimes and extra fields must serialize
recursively; API aliases are used by default.

`BaseModel.construct(**values)` creates an unvalidated model while recursively
constructing nested annotated models, lists, optional values and mappings.
`openai._models.construct_type(type_, value)` performs the corresponding
recursive conversion for a supplied type. Normal construction retains
Pydantic validation errors.

### Query strings

`openai._qs.stringify(params, *, array_format="repeat",
nested_format="brackets")` returns URL-encoded query text and omits `None` and
empty mappings. Primitive booleans are lowercase `true`/`false`. Nested
mappings use bracket keys by default or dotted keys with `nested_format="dots"`.
Arrays support `repeat`, `comma`, and `brackets`; unknown formats raise
`NotImplementedError`. `Querystring(...).stringify`, `.stringify_items`, and
`.parse` expose the same behavior.

### Server-Sent Events

`openai._streaming.ServerSentEvent` exposes `event`, `data`, `id`, `retry`, and
`json()`. `SSEDecoder.iter_bytes(iterator)` accepts arbitrarily fragmented
bytes and yields events at blank lines. `SSEDecoder.aiter_bytes(async_iterator)`
does the same asynchronously. Support LF, CR, and CRLF, comments beginning
with `:`, repeated `data:` lines joined with newlines, `id:` persistence, and
integer `retry:` values. Invalid/unknown fields are ignored, an unterminated
final line is processed, and decoder state is reset after iteration.

### Webhooks

`openai.lib._webhooks.webhook_signature_matches(payload, headers, *, secret,
tolerance)` accepts text or UTF-8 bytes and case-insensitive required headers
`webhook-id`, `webhook-timestamp`, and `webhook-signature`. Verify the HMAC
SHA-256 signature over `webhook_id.timestamp.payload`, using either a raw
secret or a `whsec_` base64 secret. Accept bare signatures, `v1,` signatures,
and any matching value in a space-separated header. Reject timestamps outside
the tolerance with `InvalidWebhookSignatureError`; malformed/missing headers
use the documented `ValueError` or typed signature error.

`OpenAI(..., webhook_secret=...)` exposes `client.webhooks.verify_signature`
and `.unwrap(payload, headers, *, secret=None)`. The latter verifies then
returns a typed `BaseModel` webhook event constructed from the JSON object;
its discriminator and additional fields remain available as attributes and
through `to_dict()`. `AsyncOpenAI.webhooks.verify_signature` follows the same
synchronous signature-verification contract.

### Clients and injected transport

`OpenAI(*, api_key, base_url="https://api.openai.com/v1", organization=None,
project=None, webhook_secret=None, timeout=None, max_retries=2,
default_headers=None, default_query=None, http_client=None)` stores the
configuration, uses a trailing-slash base URL, and returns bearer
authentication headers. `OpenAI.copy(...)` returns an independent client;
provided headers/query values merge over existing values, while
`set_default_headers` and `set_default_query` replace them. Supplying both a
merge and replacement option raises `ValueError`.

`client.get(path, *, cast_to, options={}, stream=False, stream_cls=None)`
performs a GET through the injected `httpx2.Client`. `options` may contain
`params` and `headers`; those values merge with client defaults without
mutating client state. `cast_to=httpx2.Response` returns the raw response.
`AsyncOpenAI` provides the same configuration and an awaitable `get` through
`httpx2.AsyncClient`. Both clients expose `is_closed`, `close`/`aclose`, and
context-manager cleanup. The tests use only in-memory transports, so a correct
implementation must not make external requests.

## Implementation Notes

Keep modules small and preserve the public import paths above. Use Pydantic's
public APIs for validation and JSON serialization, `urllib.parse` for URL
encoding, and bounded incremental buffering for SSE. Header lookup must be
case-insensitive, signature comparison must use constant-time comparison, and
error messages must not include secrets or payloads. The generated endpoint
resources, live service calls, Azure/Bedrock providers, realtime websockets,
TLS/mTLS, file uploads, proxy integration, optional transports, and repository
release tooling are outside this offline contract.

## Examples

```python
from openai import BaseModel, NOT_GIVEN
class Item(BaseModel):
    name: str
item = Item(name='one')
item.to_dict()
```

```python
from openai._qs import stringify
stringify({'filter': {'active': True}, 'tag': ['a', 'b']})
```

```python
from openai._streaming import SSEDecoder
events = list(SSEDecoder().iter_bytes([b'data: {"ok":true}\n\n']))
```

## Error Handling and Boundary Conditions

- Pydantic validation errors remain typed and unknown fields remain available
  as documented extras.
- Query formats outside `repeat`, `comma`, and `brackets`, or unsupported
  nested formats, raise the documented errors.
- SSE input may be fragmented and use LF, CR, or CRLF; invalid fields are
  ignored, while body reads and webhook signatures retain their typed errors.
- Webhook timestamps outside tolerance and mismatched signatures are rejected
  without exposing secrets or payloads in errors.
- HTTP requests use only injected in-memory transports; no endpoint, DNS,
  credential, or external network access is allowed.
