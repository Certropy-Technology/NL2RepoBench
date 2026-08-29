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

