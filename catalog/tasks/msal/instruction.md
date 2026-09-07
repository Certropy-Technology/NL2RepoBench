# Build `msal`

## Project Description

Create the `msal` project from an empty workspace. This is a repository-generation task for the frozen `python` package contract, task specification version `1.0.0`, at source revision `1416438a14118949d05be634124ab5d1c94c1f99`. Implement the public behavior described by the local inventories and the task-specific detail below; do not copy upstream source or tests. The supported scope is python, oauth2, openid-connect, token-cache, security, offline, separate-verifier.

## Natural Language Instruction

Starting with an empty `workspace/`, create an installable `msal` project. Implement every public/core API named in the API Usage Guide, its package exports, and its documented integration points. Preserve observable input types, return shapes, ordering, determinism, state changes, and documented exception behavior. The project must be usable through its declared `msal` import path (or the package root for this Node task), and all required modules must be present in the directory structure below.

The task-specific specification retained below supplies the detailed behavior for each API family. Treat it as the contract: do not add unrelated APIs, replace deterministic behavior with randomized or time-dependent behavior, or weaken error handling.

## Supports

- Language/runtime: `python` on `3.12.11`; target environment metadata declares `debian-12-amd64`.
- Distribution/package: `msal`; import/root name: `msal`. Package manager: `pip`.
- Install from the repository root with `python -m pip install . --no-deps`. Build metadata must be complete and agree with the package entry point.
- Dependency status in the frozen source metadata is `known`. Use only dependencies declared by the task and available in the preinstalled build image; standard-library modules are not third-party runtime dependencies.
- NoNetwork boundary: agent, candidate, verifier, Oracle, and controls run with `network_mode=no-network`. Do not access GitHub, PyPI, npm registries, Go proxy, DNS, or external services at runtime. Do not fetch source or dependencies during implementation or package use.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── msal/
│   └── __init__.py
└── README.md
```

The tree is the minimum public project layout. Add a module only when it corresponds to a documented import path or package resource. Do not place publicly unavailable evaluator code, non-public evaluation material, Oracle payloads, dependency caches, or trusted reports in this workspace.

## API Usage Guide

The public/core API families recorded in the local inventory are: Authority helpers, OAuth/OIDC request and claim helpers, Token cache, Response, throttling, authentication, and XML helpers.

For each listed family, the detailed contract below defines the import path or CLI entry, signature, accepted inputs, return type/shape, ordering and determinism, state or I/O side effects, errors, and examples. Implement the complete public surface, including root re-exports and aliases where the specification names them. If an API is stateful, preserve mutation and repeated-call behavior; if it is pure, do not introduce global state.

## Implementation Notes

Keep the implementation self-contained and deterministic under the declared runtime. The candidate repository must install from the workspace root, import through the documented public path, and run without external services. Preserve package metadata, module semantics (ESM/CommonJS or Python import behavior), serialization formats, resource cleanup, and boundary behavior described below. publicly unavailable evaluator adapters and non-public evaluation details are not part of the implementation.

## Examples

Ordinary project examples:

```bash
cd workspace
python -m pip install . --no-deps
```

```python
# Import the public package and use the task-specific APIs documented below.
from msal import *
```

The retained task-specific examples below provide ordinary API calls and combinations grounded in the frozen inventory. Keep their result shapes and ordering exact.

## Error Handling and Boundary Conditions

- Empty inputs, malformed values, missing resources, duplicate values, and unsupported options must follow the task-specific error contracts below; do not silently coerce or discard information unless explicitly specified.
- Repeated calls must remain deterministic. Filesystem, process, clock, random, native, callback, and serialization boundaries are supported only where the local specification documents them.
- Network attempts are prohibited and must not be used as a fallback. Installation failures, missing offline dependencies, or unsupported external capabilities are environment/source concerns, not reasons to invent behavior.


## Source-derived task detail

# Build `msal`

Recreate the installable public behavior of the pinned `msal` Python package
from an empty workspace. The result must be a normal PEP 517 or legacy
setuptools project that installs as the distribution `msal` and exposes the
documented package imports.

## Project Description

MSAL Python provides OAuth 2.0 and OpenID Connect client building blocks for
Microsoft identity platforms. This task assesses a deterministic offline core:
authority URL handling, authorization-request construction, JWT claim decoding,
token-cache storage and persistence, retry/throttling response helpers, and
small protocol utilities. The evaluator never contacts Azure, an IMDS endpoint,
an HTTP service, a broker, a browser, or a DNS server.

## Supports

- Use CPython 3.12 on Linux and install the distribution as `msal`.
- Runtime dependencies may be imported from the preinstalled environment:
  `requests`, `PyJWT[crypto]`, and `cryptography`.
- Preserve the package version `msal.__version__ == "1.38.0"` and the public
  top-level exports `ClientApplication`, `PublicClientApplication`,
  `ConfidentialClientApplication`, `TokenCache`, `SerializableTokenCache`,
  `PopAuthScheme`, `AutoRefresher`, `Prompt`, `IdTokenError`, and
  `BrowserInteractionTimeoutError`.
- The submitted repository must install without Git metadata and without
  fetching anything during candidate or verifier execution.

The assessed contract intentionally excludes live tenant discovery and token
acquisition, device/browser interaction, broker or native runtime integration,
managed identity endpoints, client certificates/private keys, and test secrets.
Those surfaces must remain importable where they are part of the documented
package layout, but no external service is required to implement them.

## API Usage Guide

### Authority helpers

`msal.authority.canonicalize(authority_or_auth_endpoint)` accepts an HTTPS URL
with a hostname and tenant path and returns `(parsed_url, hostname, tenant)`.
It preserves the parsed URL, lowercases the hostname, and raises `ValueError`
for non-HTTPS, hostless, or tenantless input. CIAM hosts use the first path
segment when present and otherwise derive the tenant from the subdomain.

`msal.authority.AuthorityBuilder(instance, tenant)` strips trailing/leading
slashes and renders as `https://{instance}/{tenant}`. The module constants for
well-known Microsoft hosts and `WORLD_WIDE` must be available.

### OAuth/OIDC request and claim helpers

`msal.oauth2cli.oauth2.Client(configuration, client_id, ...)` accepts a
configuration dictionary and an injected HTTP client. Its
`build_auth_request_uri(response_type, redirect_uri=None, scope=None,
state=None, **kwargs)` returns a URL-encoded authorization URL. It preserves
the provided response type, redirect URI, state, scope and extra parameters;
list scopes are joined with spaces. `initiate_auth_code_flow(...)` returns a
JSON-safe dictionary containing an authorization URI, state, and PKCE values.

`msal.oauth2cli.oidc.decode_part(raw, encoding="utf-8")` decodes padded or
unpadded base64url text; with `encoding=None` it returns bytes. The obsolete
alias `base64decode` has the same behavior. `decode_id_token(id_token, ...)`
returns the JSON payload and performs the documented legacy issuer, audience,
nonce, and expiry checks. `Prompt` exposes `NONE`, `LOGIN`, `CONSENT`,
`SELECT_ACCOUNT`, and `CREATE` string constants.

### Token cache

`msal.TokenCache()` stores JSON-like access-token, refresh-token, ID-token,
account, and app-metadata entries. `add(event, now=None)` normalizes sorted
scopes, authority environment/realm, timestamps, client information, and token
entries. `search(credential_type, target=None, query=None, *, now=None)` is a
generator of matching entries; access tokens require all requested target scopes
and expired access tokens are removed. `find(...)` returns the same results as a
list and may emit its documented deprecation warning.

`SerializableTokenCache` adds `serialize() -> str` and
`deserialize(state) -> None`, with `has_state_changed` set after mutation and
cleared by serialization/deserialization. `remove_at`, `remove_rt`,
`remove_idt`, `remove_account`, and `modify` update the corresponding cache
entries.

`msal.token_cache._compute_ext_cache_key(data)` is a stable lowercase base64url
SHA-256 key for non-standard request fields. Standard OAuth fields are ignored,
key order does not matter, and different extra values produce different keys.
`_parse_claims_or_raise` accepts only a JSON object and raises a friendly
`ValueError` without including malformed or sensitive input. `_merge_claims`
recursively merges two JSON objects, with the second value winning at leaf
conflicts.

### Response, throttling, authentication, and XML helpers

`msal.throttled_http_client.RetryAfterParser.parse(result=...)` returns a bounded
integer delay for HTTP 429/5xx or an explicit case-insensitive `Retry-After`
header, using its configured default when the header is missing or invalid.
`NormalizedResponse` copies status, text, and lowercase headers and raises
`MsalServiceError` for status >= 400.

`msal.auth_scheme.PopAuthScheme(http_method, url, nonce)` accepts only the
uppercase methods GET, POST, PUT, DELETE, and PATCH and preserves the parsed URL
and nonce fields. `msal.wstrust_request.escape_xml` escapes XML text and
`wsu_time_format` formats a UTC timestamp in the package's wire representation.

All assessed returns are JSON-safe or are converted by the verifier adapter.
Preserve deterministic ordering and exact exception classes for the documented
invalid-input cases. Do not add network calls, wall-clock assertions, random
test dependencies, or writes outside the candidate workspace.

## Implementation Notes

- Keep the package import paths and re-exports compatible with the pinned
  revision. A conventional `setup.py` plus `setup.cfg`, `pyproject.toml`, or
  equivalent build backend is acceptable.
- Separate candidate code from test code. The evaluator installs your package
  into a candidate-owned target and invokes behavior through isolated child
  processes.
- Cache serialization must round-trip without changing JSON values, and cache
  key generation must be independent of dictionary insertion order.
- Authorization request generation may use unpredictable state/PKCE values;
  the evaluator checks shape, encoding, and relationships rather than a fixed
  random string.
- Never implement live identity-provider behavior by contacting a service.

