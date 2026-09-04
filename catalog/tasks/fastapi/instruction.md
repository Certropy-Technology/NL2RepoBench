# Build `fastapi`

Create an installable Python package named `fastapi`, version `0.141.1`, from
an empty workspace. Implement the deterministic framework behavior below.
Evaluation uses CPython 3.12 on Debian amd64 with no runtime network access.

## Project Description

FastAPI is an ASGI application framework that combines Starlette routing and
responses with Pydantic validation and OpenAPI generation. This task covers
application and router construction, parameter metadata, JSON-compatible
encoding, security descriptors, exception records, deterministic OpenAPI,
server-sent-event formatting, and selected Starlette re-exports. It excludes
live servers, sockets, browser clients, multipart parsing, templates, external
services, and filesystem delivery.

## Supports

- A normal `pyproject.toml` project containing a `fastapi/` package and
  `fastapi/py.typed`.
- `fastapi.__version__ == "0.141.1"`.
- CPython 3.12 with Pydantic 2.13, Starlette 1.6, AnyIO, `annotated-doc`,
  `typing-extensions`, and `typing-inspection` available.
- In-memory ASGI metadata and deterministic JSON/OpenAPI values only.
- No source download, dependency installation, DNS lookup, outbound request,
  external process, credential lookup, or live service during evaluation.

## API Usage Guide

### Public package and application

`fastapi.FastAPI(*, debug=False, routes=None, title="FastAPI",
summary=None, description="", version="0.1.0", openapi_url="/openapi.json",
openapi_tags=None, servers=None, dependencies=None,
default_response_class=Default(JSONResponse), redirect_slashes=True,
docs_url="/docs", redoc_url="/redoc", swagger_ui_oauth2_redirect_url=
"/docs/oauth2-redirect", **configuration) -> FastAPI` constructs an ASGI
application. The public attributes `title`, `summary`, `description`,
`version`, `routes`, and `openapi_schema` preserve configuration. Setting a
documentation URL to `None` disables that route.

`app.get(path, **route_options)`, `app.post(path, **route_options)`, and the
other HTTP method decorators register the decorated sync or async callable.
The resulting route preserves `path`, `methods`, `name`, `tags`, `summary`,
`status_code`, and response metadata. `app.include_router(router, *, prefix="",
tags=None, dependencies=None, responses=None, deprecated=None,
include_in_schema=True, **options)` includes the router under the combined
prefix. Prefixes start with `/` and cannot end with `/`.

`app.url_path_for(name: str, **path_params) -> URLPath` reverses a named route,
serializing path parameters and raising `NoMatchFound` when no route matches.

`app.openapi() -> dict[str, Any]` lazily produces and caches an OpenAPI 3.1
document. It includes application info, configured tags and servers, route
paths/methods, operation IDs, parameter schemas, response schemas, and
security components. Repeated calls return the cached `openapi_schema` object.
Generated operation IDs use the endpoint name, normalized route path, and
lowercase method, for example `read_value_a_b__x__get`.

### Routers

`fastapi.APIRouter(*, prefix="", tags=None, dependencies=None,
default_response_class=Default(JSONResponse), responses=None, callbacks=None,
routes=None, redirect_slashes=True, default=None, dependency_overrides_provider
=None, route_class=APIRoute, **options) -> APIRouter` groups routes. Its
`get`, `post`, and other method decorators have the same registration behavior
as the application. Included router prefixes and tags are composed in order;
OpenAPI exposes the final path and declared status response.

### Parameter and dependency declarations

The functions below return Pydantic `FieldInfo`-compatible metadata objects.
They preserve `default`, `alias`, `title`, `description`, validation keywords,
`deprecated`, and `include_in_schema` where applicable:

- `Path(default=..., *, alias=None, title=None, description=None, gt=None,
  ge=None, lt=None, le=None, min_length=None, max_length=None, pattern=None,
  strict=None, deprecated=None, include_in_schema=True, **extra) -> params.Path`.
  Path parameters are always required and expose `in_.value == "path"`.
- `Query(default=..., *, alias=None, title=None, description=None, gt=None,
  ge=None, lt=None, le=None, min_length=None, max_length=None, pattern=None,
  strict=None, deprecated=None, include_in_schema=True, **extra) -> params.Query`.
- `Header(...) -> params.Header` and `Cookie(...) -> params.Cookie` use the
  same metadata model for their request locations.
- `Body(default=..., *, embed=None, media_type="application/json", alias=None,
  title=None, description=None, **validation) -> params.Body` preserves
  `embed` and media type.
- `Form(default=..., *, media_type="application/x-www-form-urlencoded",
  **metadata) -> params.Form`; `File(default=..., *, media_type=
  "multipart/form-data", **metadata) -> params.File`.

`Depends(dependency=None, *, use_cache=True, scope=None) -> params.Depends`
stores the callable, caching flag, and optional `"function"` or `"request"`
scope. `Security(dependency=None, *, scopes=None, use_cache=True) ->
params.Security` additionally stores an ordered list of OAuth scopes.

### Encoding and utility behavior

`fastapi.encoders.jsonable_encoder(obj, include=None, exclude=None,
by_alias=True, exclude_unset=False, exclude_defaults=False, exclude_none=False,
custom_encoder=None, sqlalchemy_safe=True) -> JSON-compatible value` recursively
converts Pydantic models, dataclasses, enums, paths, UUIDs, dates/times,
timedeltas, decimals, bytes, mappings, and iterables. Date/time values use ISO
format; timedeltas use total seconds; integral decimals become integers and
fractional decimals become floats. `include`/`exclude` filter mapping/model
fields. A matching `custom_encoder` type takes precedence.

`fastapi.datastructures.Default(value) -> DefaultPlaceholder` wraps framework
defaults. The wrapper exposes `.value`, delegates truthiness to it, and compares
equal when wrapped values compare equal.

`fastapi.utils.is_body_allowed_for_status_code(status_code) -> bool` rejects
body content for informational, 204, and 304 responses.
`get_path_param_names(path: str) -> set[str]` returns text found between route
braces, including an explicit convertor suffix. `deep_dict_update(main_dict,
update_dict) -> None` recursively merges dictionaries and concatenates lists
when both existing and incoming values are lists. `get_value_or_default(first,
*extra)` returns the first value that is not a `DefaultPlaceholder`, falling
back to the first item.

### Exceptions

`fastapi.HTTPException(status_code: int, detail: Any = None, headers: dict |
None = None)` preserves those public attributes.
`RequestValidationError(errors, *, body=None)`,
`WebSocketRequestValidationError(errors)`, and
`ResponseValidationError(errors, *, body=None, endpoint_ctx=None)` preserve
the error list returned by `.errors()` and relevant body/context metadata.

### Security helpers

`APIKeyHeader(*, name: str, scheme_name=None, description=None,
auto_error=True)` reads the named request header when awaited with a Starlette
`Request`. A missing value raises HTTP 401 with detail `"Not authenticated"`
when `auto_error` is true, otherwise it returns `None`. Its OpenAPI model uses
the header location.

`HTTPBasic(*, scheme_name=None, realm=None, description=None, auto_error=True)`
parses `Authorization: Basic ...` into `HTTPBasicCredentials(username,
password)`. `HTTPBearer(..., bearerFormat=None, auto_error=True)` parses a
Bearer header into `HTTPAuthorizationCredentials(scheme, credentials)`.
Malformed or missing mandatory credentials raise HTTP 401.

`OAuth2PasswordRequestForm(*, grant_type=None, username, password, scope="",
client_id=None, client_secret=None)` stores the form fields and splits the
space-delimited scope into `.scopes`. `SecurityScopes(scopes=None)` preserves
the ordered list and exposes `.scope_str` joined by one space.

`get_authorization_scheme_param(authorization_header_value) -> tuple[str,str]`
splits once at the first space; absent input returns `("", "")`.

### SSE, responses, middleware, and background tasks

`ServerSentEvent(*, data=None, raw_data=None, event=None, id=None, retry=None,
comment=None)` validates that `event` and `id` contain no CR/LF. The keyword-only
`format_sse_event(*, data_str=None, event=None, id=None, retry=None,
comment=None) -> bytes` emits fields in event, data-line, id, retry, comment
order and terminates the event with a blank line. Multiline data produces one
`data:` line per input line. `KEEPALIVE_COMMENT` is the bytes heartbeat frame.

`fastapi.responses` re-exports Starlette `Response`, `JSONResponse`,
`HTMLResponse`, `PlainTextResponse`, `RedirectResponse`, `StreamingResponse`,
and `FileResponse`; their deterministic in-memory behavior follows Starlette.
The middleware modules similarly re-export `CORSMiddleware`, `GZipMiddleware`,
`HTTPSRedirectMiddleware`, `TrustedHostMiddleware`, and `WSGIMiddleware`.

`BackgroundTasks(tasks=None)` extends Starlette’s collection. `add_task(func,
*args, **kwargs)` appends a sync or async callback, and awaiting the collection
runs callbacks in insertion order.

## Implementation Notes

Preserve normal import paths and public object types. Route, parameter, and
OpenAPI ordering is deterministic and follows registration order. Async
security and background helpers must remain awaitable. The verifier executes
bounded scenarios in an unprivileged child process and never imports candidate
code into the trusted grading process. Optional CLI/cloud tooling, live HTTP or
WebSocket transports, templates, multipart bodies, database integrations,
filesystem serving, and external identity providers are outside this contract.
