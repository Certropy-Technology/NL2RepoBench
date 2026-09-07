# Project Description

Build a clean-room Python distribution named `google-genai` that implements the
offline, deterministic core of the Google Gen AI SDK. The package represents
typed request/response content, coerces convenient content inputs, exposes
local chat history and pager state, and provides deterministic HTTP option and
error helpers. It must install from an empty workspace and expose the
`google.genai` namespace.

This task does not require API credentials, a Google Cloud project, model
inference, file uploads, WebSockets, MCP, tokenization, or any network request.
Network-facing client methods are outside the scored contract.

# Supports

- Python 3.12 on Linux.
- A normal `pip install .` using any PEP 517 backend available in the supplied
  environment. Distribution metadata must use name `google-genai` and version
  `2.20.0`.
- Runtime dependencies from the supplied offline environment, including
  Pydantic 2, `google-auth`, HTTPX, Requests, AnyIO, Tenacity, WebSockets,
  `typing-extensions`, `distro`, and `sniffio`.
- Imports `google.genai`, `google.genai.types`, `google.genai.errors`,
  `google.genai.chats`, `google.genai.pagers`, `google.genai._transformers`,
  `google.genai._api_client`, and `google.genai._common`.
- Root exports `Client`, `types`, and `errors`. `Client` only needs to remain an
  importable SDK surface for this offline task; no remote request behavior is
  scored.

## Natural Language Instruction

Create the installable `google-genai` distribution from an empty workspace.
Implement typed parts/content and coercion, local HTTP/common helpers, API
errors, response accessors, chat history, and synchronous/asynchronous pagers
using the exact imports and signatures below. Network-facing client behavior is
excluded.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
└── google/
    └── genai/
        ├── __init__.py
        ├── types.py
        ├── errors.py
        ├── chats.py
        ├── pagers.py
        ├── _transformers.py
        ├── _api_client.py
        └── _common.py
```

Preserve Pydantic-compatible models, root exports, and module paths. Do not
include replay data, internal tests, credentials, or remote-service code.

## Examples

```python
from google.genai import types
part = types.Part.from_text(text='hello')
content = types.UserContent(parts=part)
```

```python
from google.genai._common import recursive_dict_update
target = {'Timeout': {'seconds': 1}}
recursive_dict_update(target, {'timeout': {'nanos': 5}})
```

## Error Handling and Boundary Conditions

Preserve positional/keyword part conflicts, unsupported coercion types, enum
case handling, base64 serialization, missing response candidates, pickle-safe
API errors, invalid chat roles, pager exhaustion, deep-copy configuration, and
async ordering. Imports and all scored operations must remain offline.

# API Usage Guide

## Typed parts and content

In `google.genai.types`, implement Pydantic-compatible models whose
`model_dump(mode="json", exclude_none=True)` output uses the field names shown
below. Binary fields serialize as standard base64 text.

`Part` supports this constructor and factories:

```text
Part(value=None, /, *, video_metadata=None, thought=None, inline_data=None,
     file_data=None, thought_signature=None, function_call=None,
     code_execution_result=None, executable_code=None,
     function_response=None, text=None, **kwargs)
Part.from_text(*, text: str) -> Part
Part.from_bytes(*, data: bytes, mime_type: str, media_resolution=None) -> Part
Part.from_uri(*, file_uri: str, mime_type: str | None = None,
              media_resolution=None) -> Part
Part.from_function_call(*, name: str, args: dict) -> Part
Part.from_function_response(*, name: str, response: dict,
                            parts: list | None = None) -> Part
Part.from_executable_code(*, code: str, language: Language) -> Part
Part.from_code_execution_result(*, outcome: Outcome, output: str) -> Part
```

- `Part.from_text(text="hello")` dumps as `{"text": "hello"}`.
- `Part.from_bytes(data=b"abc", mime_type="text/plain")` places base64
  `YWJj` and the MIME type under `inline_data`.
- `Part.from_uri(file_uri="gs://bucket/cat.png")` places the URI under
  `file_data` and infers `image/png` when `mime_type` is omitted.
- Function call/response factories create nested `function_call` and
  `function_response` objects while preserving JSON arguments.
- Executable code and execution results preserve enum values such as `PYTHON`
  and `OUTCOME_OK`.
- A positional string is shorthand for a text part. Supplying a positional
  value together with keyword fields raises `ValueError` with a clear conflict
  message.

Provide `Content(role=None, parts=None)`, plus:

```text
UserContent(parts: Part-compatible value or list) -> UserContent
ModelContent(parts: Part-compatible value or list) -> ModelContent
```

They normalize one value to a list and force roles `user` and `model`
respectively. Export the supporting models used in dumps, including `Blob`,
`FileData`, `FunctionCall`, `FunctionResponse`, `ExecutableCode`, and
`CodeExecutionResult`. String enum construction is case-insensitive; for
example `HarmCategory("harm_category_hate_speech")` resolves to
`HARM_CATEGORY_HATE_SPEECH`.

## Content coercion

Implement these helpers in `google.genai._transformers`:

```text
t_part(part) -> Part | None
t_parts(parts) -> list[Part] | None
t_content(content) -> Content | None
t_contents(contents) -> list[Content] | None
```

Strings become text parts. Part dictionaries are validated as `Part` objects.
`t_content("hello")` becomes one user content. `t_contents` groups consecutive
user parts, maps function-call parts to model content, and maps function
responses to user content. A later ordinary text part remains in the current
user group. Unsupported values such as integers raise `ValueError` identifying
the unsupported type. Preserve explicit `Content` objects and input order.

## HTTP option and dictionary helpers

In `google.genai._api_client`, provide:

```text
join_url_path(base_url: str, path: str) -> str
patch_http_options(options: HttpOptions, patch_options: HttpOptions) -> HttpOptions
populate_server_timeout_header(headers: dict[str, str],
                               timeout_in_seconds: float | int | None) -> None
```

`join_url_path` produces exactly one slash at the boundary without stripping a
base trailing slash when the path is empty. `patch_http_options` returns an
independent merged `HttpOptions`: non-null patch fields replace base fields,
headers merge by key, and inputs are not mutated. `HttpOptions` supports at
least `base_url`, `api_version`, `headers`, `timeout`, and `retry_options`.
The timeout helper writes `X-Server-Timeout` as rounded-up whole seconds and
does not overwrite an existing header.

In `google.genai._common`, provide:

```text
align_key_case(target_dict: dict, update_dict: dict) -> dict
recursive_dict_update(target_dict: dict, update_dict: dict) -> None
```

Key matching is case-insensitive and ignores underscores. Alignment returns a
new recursively aligned update dictionary. Recursive update mutates the target,
merges nested dictionaries, aligns key casing, and replaces scalar values.

## API errors

In `google.genai.errors`, implement:

```text
APIError(code: int | None, response_json, response=None)
APIError.raise_error(status_code: int, response_json, response) -> None
ClientError(APIError)
ServerError(APIError)
```

Read `code`, `message`, and `status` from either the top level or an `error`
object. An explicit nonzero `code` wins. The string form is
`"<code> <status>. <details>"`. Statuses 400-499 raise `ClientError`, statuses
500-599 raise `ServerError`, and other statuses raise `APIError`. Instances
must survive a pickle round trip with type, fields, and string form intact.

## Generate-content response accessors

`GenerateContentResponse(candidates=None, ...)` exposes read-only properties:

```text
response.parts -> list[Part] | None
response.text -> str | None
response.function_calls -> list[FunctionCall] | None
```

Use only the first candidate. `text` concatenates its text parts in order,
`parts` returns all parts, and `function_calls` returns only non-null function
calls. Missing candidates/content/parts return `None`.

## Local chat history

In `google.genai.chats`, provide:

```text
Chat(*, modules, model: str, config=None, history: list[Content | dict])
Chat.get_history(curated: bool = False) -> list[Content]
Chat.record_history(user_input: Content, model_output: list[Content],
                    is_valid: bool) -> None
```

The comprehensive history retains every turn. The curated history contains
valid user/model exchanges only: a model content with no parts invalidates
itself and its preceding unmatched user turn. Roles other than `user` or
`model` raise `ValueError`. `record_history` always extends comprehensive
history and extends curated history only when `is_valid` is true.

## Pagers

In `google.genai.pagers`, implement:

```text
Pager(name, request, response, config)
AsyncPager(name, request, response, config)
```

The response exposes an attribute named by `name`, `next_page_token`, and
optionally `sdk_http_response`. Both pagers expose `page`, `name`, `page_size`,
`sdk_http_response`, `config`, indexing, and current-page length. They deep-copy
the input config, add the response token as `page_token`, and preserve the
requested `page_size`. Iteration transparently requests subsequent pages with
`request(config=...)`. `next_page()` raises
`IndexError("No more pages to fetch.")` when the token is false. `AsyncPager`
uses awaitable requests and asynchronous iteration with the same semantics.

# Implementation Notes

- Keep namespace/package metadata conventional and include all modules needed
  by the imports above. Do not include internal tests, grading code, reward files,
  or a source archive.
- Preserve deterministic ordering in lists and serialized mappings. Do not
  contact remote services or read credentials as part of import or the scored
  APIs.
- Pydantic validation exceptions are acceptable for malformed typed model
  inputs unless a specific `ValueError` contract is stated above.
- The evaluator installs the workspace with `pip --no-deps
  --no-build-isolation` into a candidate-owned target. Build and runtime
  dependencies are already available from a hash-locked image closure.
- Every scored operation runs in an isolated unprivileged subprocess. Do not
  depend on state left by a previous verifier call.
