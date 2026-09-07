# Build `google-api-core`

Create a complete installable Python distribution named `google-api-core`,
version `2.35.0`, from an empty workspace. The import package is
`google.api_core`. Reproduce the deterministic public behavior below without
using a preinstalled `google-api-core` package, source checkout, network access,
or service credentials at runtime.

## Project Description

`google-api-core` supplies shared helpers used by generated Google API clients:
client metadata and options, URL path and REST serialization, protobuf field
helpers, error translation, retry and timeout policies, page iteration, and
universe-domain endpoint selection. The task measures this deterministic core,
not a live Google Cloud client or a transport integration.

## Supports

- CPython 3.12 on Linux amd64 with a normal PEP 517/setuptools install.
- Distribution metadata must report `google-api-core` version `2.35.0`.
- Import paths under `google.api_core` must be real packages and include
  `google/api_core/py.typed`.
- Runtime dependencies may include `googleapis-common-protos`, `protobuf`,
  `proto-plus`, `google-auth`, and `requests`, but the project must not fetch
  them at runtime. The supplied verifier image already has the exact offline
  dependency closure.
- Do not add tests, verifier code, reward files, source archives, network
  downloads, or cloud credentials to the candidate package.
- Keep behavior deterministic under `PYTHONHASHSEED=0`, `LC_ALL=C.UTF-8`,
  `TERM=dumb`, and `CI=true`. Do not sleep or depend on the current time in
  ordinary helper behavior.

## Natural Language Instruction

Create the installable `google-api-core` distribution from an empty workspace.
Implement the local metadata/options, datetime and path helpers, exception and
universe selection, retry/timeout, protobuf/page iteration, and version-header
surfaces listed below. Preserve import paths, typed message behavior, and
deterministic serialization.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
└── google/
    └── api_core/
        ├── __init__.py
        ├── client_info.py
        ├── client_options.py
        ├── datetime_helpers.py
        ├── exceptions.py
        ├── page_iterator.py
        ├── path_template.py
        ├── protobuf_helpers.py
        ├── rest_helpers.py
        ├── retry.py
        ├── timeout.py
        ├── universe.py
        ├── version_header.py
        └── py.typed
```

Every module named in the API guide must be importable under
`google.api_core`; optional transport dependencies must not break deterministic
imports. Do not include private evaluation files.

## Examples

```python
from google.api_core import datetime_helpers, path_template
stamp = datetime_helpers.to_rfc3339(datetime_helpers.utcnow())
name = path_template.expand('v1/{name=projects/*}', name='projects/demo')
```

```python
from google.api_core import rest_helpers
pairs = rest_helpers.flatten_query_params({'filter': {'state': ['A', 'B']}})
```

## Error Handling and Boundary Conditions

Preserve UTC/offset and nanosecond handling, path traversal rejection, missing
fields, strict flattening errors, HTTP/gRPC status mapping, universe mismatch,
retry predicates, injected-clock timeouts, protobuf type checks, page exhaustion,
and optional-import behavior. No runtime request, credential lookup, DNS, or
network access is allowed.

## API Usage Guide

### Package and client metadata

`google.api_core.__version__` is the string `"2.35.0"`. The package must expose
the documented modules without requiring grpcio or aiohttp.

`google.api_core.client_info.ClientInfo(python_version=_PY_VERSION,
grpc_version=None, api_core_version=_API_CORE_VERSION,
gapic_version=None, client_library_version=None, user_agent=None,
rest_version=None, protobuf_runtime_version=None)` stores the supplied values.
`to_user_agent()` returns a single space-separated string in this order:
optional user-agent prefix, `gl-python/...`, optional `grpc/...`, optional
`rest/...`, `gax/...`, optional `gapic/...`, optional `gccl/...`, and optional
`pb/...`. It omits absent values and has no trailing space.

`google.api_core.client_options.ClientOptions(api_endpoint=None,
client_cert_source=None, client_encrypted_cert_source=None,
quota_project_id=None, credentials_file=None, scopes=None, api_key=None,
api_audience=None, universe_domain=None)` stores these public attributes.
Supplying both certificate callbacks raises `ValueError`; supplying both
`credentials_file` and `api_key` raises `ValueError`. `repr(options)` is a
deterministic `ClientOptions: ` prefix followed by the instance dictionary.
`from_dict(mapping)` returns an equivalent `ClientOptions` and raises
`ValueError` for an unknown option.

### Datetime helpers

In `google.api_core.datetime_helpers`, `to_milliseconds(datetime)` and
`to_microseconds(datetime)` return integer Unix offsets. Naive datetimes are
treated as UTC; aware datetimes are converted to UTC. `from_microseconds(value)`
returns a UTC-aware datetime. `from_iso8601_date` and `from_iso8601_time` parse
their ISO forms. `from_rfc3339(text)` accepts a UTC `Z` or numeric offset and
fractional seconds, returning a UTC-aware datetime. `to_rfc3339(datetime)`
returns canonical UTC RFC3339 text and preserves microseconds when nonzero.
`DatetimeWithNanoseconds` retains a nanosecond remainder and serializes through
`rfc3339()` with up to nine fractional digits. Invalid RFC3339 forms raise
`ValueError`.

### Path templates and REST serialization

`google.api_core.path_template.expand(tmpl, *args, **kwargs)` replaces
positional `*`/`**` and named `{name}`, `{name=*}`, `{name=**}`, or subtemplate
variables. Missing variables raise `ValueError`. A wildcard value must not
contain `.` or `..` path segments. `get_field(mapping_or_message, "a.b",
encode=False)` reads nested fields; with `encode=True` it percent-encodes the
value while leaving `/` safe. `delete_field(request, "a.b")` removes a nested
mapping/message field. `validate(template, path)` returns whether a path matches
the template. `transcode(http_options, message=None, **request_kwargs)` accepts
HTTP rules containing `method`, `uri`, and optional `body` keys, and returns a
dictionary containing the selected method, expanded URI, body, and query
parameters. It raises `ValueError` when no rule matches the request.

`google.api_core.rest_helpers.flatten_query_params(params, strict=False)`
flattens nested dictionaries and repeated values into ordered `(key, value)`
pairs. `None` values are omitted; lists preserve order; nested keys use dot
notation. In strict mode, unsupported values raise `TypeError`.
`transcode_request(http_options, request, required_fields_default_values=None,
rest_numeric_enums=False)` accepts a protobuf or proto-plus request and returns
`(raw_transcoded_request, serialized_body_or_none, query_params)`. The first
item contains the chosen HTTP method and URI. Invalid request shapes raise
`TypeError` or `ValueError` according to the failed conversion or rule match.

```python
from google.api_core import path_template, rest_helpers

name = path_template.expand("v1/{name=projects/*}", name="projects/demo")
query = rest_helpers.flatten_query_params({"filter": {"state": ["A", "B"]}})
```

### Exceptions and universe domains

`google.api_core.exceptions` defines the HTTP and gRPC error hierarchy,
including `GoogleAPIError`, `GoogleAPICallError`, `BadRequest`, `Unauthorized`,
`Forbidden`, `NotFound`, `Conflict`, `TooManyRequests`, `InternalServerError`,
`ServiceUnavailable`, `GatewayTimeout`, and `RetryError`.
`exception_class_for_http_status(status_code)` and
`from_http_status(status_code, message, **kwargs)` map known HTTP statuses to
the corresponding class and unknown statuses to `Unknown`.
`format_http_response_error(response, method, url, payload=None)` is
deterministic, and `from_http_response(response)` handles JSON and text response
objects without contacting the network. `exception_class_for_grpc_status`
and `from_grpc_status(status_code, message, **kwargs)` perform the analogous
mapping for `grpc.StatusCode` values when gRPC is installed; an unknown value
maps to the generic call-error class.

`google.api_core.universe.get_universe_domain(*potential_universes,
default_universe)` selects the first non-`None` stripped value, or the default;
an empty result raises `EmptyUniverseError`. `determine_domain(client, env)`
uses the client value, then environment value, then `googleapis.com`.
`compare_domains(client, credentials)` returns `True` for a match and raises
`UniverseMismatchError` otherwise. `get_default_mtls_endpoint(endpoint)`
converts `service.googleapis.com` and sandbox endpoints to their `.mtls.`
forms while preserving schemes and ports. `get_api_endpoint(override,
universe_domain, default_universe, default_mtls_endpoint,
default_endpoint_template, use_mtls)` always honors an override, otherwise
selects the mTLS endpoint only for the default universe and formats
`{UNIVERSE_DOMAIN}` for ordinary endpoints.

### Retry and timeout policies

`google.api_core.retry.if_exception_type(*exception_types)` returns a predicate
that matches those exception classes. `if_transient_error` matches the
library's retryable HTTP/service exceptions. `exponential_sleep_generator(
initial, maximum, multiplier=2.0)` yields deterministic increasing delays capped
at `maximum`.

`Retry(predicate=if_transient_error, initial=1.0, maximum=60.0,
multiplier=2.0, timeout=120.0, on_error=None, **kwargs)` is callable and
retries only predicate-matching failures until its timeout. `with_timeout` and
`with_predicate` return independent policies. The `__str__` form is stable.
Tests use immediate-success and bounded retry callables only; no sleep or wall
clock is required from the implementation.

`ConstantTimeout(timeout=None)` decorates a function and supplies the exact
`timeout` keyword. `ExponentialTimeout(initial=5.0, maximum=30.0,
multiplier=2.0, deadline=None)` supplies successive timeout values and supports
`with_deadline`. `TimeToDeadlineTimeout(timeout=None, clock=utcnow)` supplies a
remaining timeout based on the injected clock. Decorators preserve function
metadata and pass through calls when timeout is `None` where the API specifies.

### Protobuf helpers, page iteration, and version headers

`google.api_core.protobuf_helpers` supports protobuf and proto-plus messages.
`get_messages(module)` discovers protobuf message classes in a module and
returns a name-to-class dictionary. `get(msg_or_dict, key, default=...)` reads a
field or returns the supplied default. `set(msg_or_dict, key, value)` updates a
field, including nested paths, and `setdefault(msg_or_dict, key, value)` only
writes when the current protobuf or mapping value is unset/falsy.
`check_oneof(**kwargs)` raises `ValueError` when more than one value is not
`None`. `field_mask(original, modified)` returns a `FieldMask` whose paths
identify changed fields in deterministic order; the two non-`None` messages
must have the same type.

`google.api_core.page_iterator.Page(parent, items, item_to_value,
raw_page=None)` exposes `num_items`, `remaining`, `raw_page`, and iteration over
converted items. `Iterator(client, item_to_value=_item_to_value_identity,
page_token=None, max_results=None)` consumes pages from a subclass-provided
`pages` property and yields items in page order, respecting `max_results`. The
corresponding async page iterator preserves the same ordering for bounded local
async generators.

`google.api_core.version_header.to_api_version_header("v1")` returns the
canonical API version metadata string and rejects unsupported input types with
the documented exception.

```python
from google.api_core import protobuf_helpers
from google.protobuf import duration_pb2

duration = duration_pb2.Duration(seconds=1)
protobuf_helpers.set(duration, "nanos", 500)
assert protobuf_helpers.get(duration, "nanos") == 500
```

## Implementation Notes

- Preserve import paths and namespace-package compatibility. Optional grpcio,
  aiohttp, and cloud transports must not make deterministic imports fail.
- Keep public signatures compatible with the frozen package. Do not replace
  structured protobuf messages with plain dictionaries where a message object
  is required.
- Error class selection, ordering, URL quoting, datetime timezone handling,
  nanosecond truncation, retry sequence, and metadata formatting are observable.
- The scored verifier is a separate no-network subprocess. Live metadata
  servers, gRPC channel construction, HTTP requests, external credential files,
  background bidi consumers, process termination, and wall-clock sleeps are
  outside this deterministic contract and must not be used to satisfy it.
