# Project Description

Create a complete, installable Python distribution named `oauthlib` from an
empty workspace. The package is a dependency-light implementation of OAuth 1.0
request signing and OAuth 2.0 request construction/parsing. The implementation
must work locally without contacting an authorization server or any other
network service.

# Natural Language Instruction

Build the complete installable `oauthlib` package from an empty workspace.
Implement the documented local OAuth 1.0 signing and OAuth 2.0 request,
response, token, and client contracts. Keep encoding, ordering, duplicate
parameters, state isolation, and typed protocol errors consistent across the
modules; do not contact an authorization server.

# Supports or Environment Configuration

- Support Python 3.9 and newer, including Python 3.12.
- Install from the repository root with `python -m pip install .` after the
  build tools supplied by the environment are available.
- Use distribution and import package name `oauthlib`, version `3.4.0`.
- The core package must have no required third-party runtime dependency.
  Optional integrations may be omitted: RSA signing needs `cryptography`,
  signed OAuth2 tokens need `cryptography` and `PyJWT`, and signals need
  `blinker`.
- Keep all behavior local and deterministic. Do not require credentials,
  services, subprocesses, files outside the installed package, or network
  access at runtime.

# Project Directory Structure

```text
workspace/
├── pyproject.toml              # package metadata and build backend
└── oauthlib/
    ├── __init__.py             # version and debug flag
    ├── common.py               # encoding, URI, request helpers
    ├── oauth1/rfc5849/          # OAuth 1.0 parameters and signatures
    └── oauth2/rfc6749/          # OAuth 2.0 clients and parameters
```

The import paths in the API guide must be real package modules. Optional RSA,
JWT, signal, and external integrations are not runtime requirements.

# API Usage Guide

The deterministic evaluator focuses on JSON-compatible calls to the following public
surface. Preserve import paths, argument order, defaults, return shapes, and
exception behavior. It also checks package metadata and the root debug flag.

## Root package

`oauthlib.__version__` is the string `"3.4.0"`. `oauthlib.set_debug(value)`
sets the package debug flag and returns `None`; `oauthlib.get_debug()` returns
the current boolean-like flag. The package installs a logging `NullHandler`
for the `oauthlib` logger.

## Common helpers

Import these from `oauthlib.common`:

```python
quote(s, safe=b'/') -> str
unquote(s) -> str
urlencode(params) -> str
urldecode(query) -> list[tuple[str, str]]
extract_params(raw) -> list[tuple[str, str]] | None
add_params_to_qs(query, params) -> str
add_params_to_uri(uri, params, fragment=False) -> str
safe_string_equals(a, b) -> bool
to_unicode(data, encoding='UTF-8') -> str | None
```

These helpers use OAuth-compatible percent encoding. `urlencode` accepts an
ordered iterable of pairs and preserves duplicate keys. `urldecode` returns
ordered pairs, decodes plus signs as spaces, and rejects malformed percent
escapes. `extract_params` accepts a query/body string or mapping-like input;
`None` remains `None`. URI helpers preserve the URI fragment and append query
parameters in order; with `fragment=True`, parameters are added to the
fragment. `safe_string_equals` compares strings without early-exit behavior.

`CaseInsensitiveDict` is a dict subclass constructed as
`CaseInsensitiveDict(data)`. String keys compare case-insensitively while the
first spelling is retained for iteration. Its `get` and `update` methods
follow normal dictionary conventions. `Request(uri, http_method='GET',
body=None, headers=None, encoding='utf-8')` exposes normalized request data,
including `uri_query()`, `uri_query_params()`, `duplicate_params`, and the
decoded body.

## OAuth 1.0 RFC 5849

Import helpers from `oauthlib.oauth1.rfc5849.utils`:

```python
filter_oauth_params(params) -> list[tuple[str, str]]
escape(value) -> str
unescape(value) -> str
parse_authorization_header(header) -> list[tuple[str, str]]
```

Import request preparation from `oauthlib.oauth1.rfc5849.parameters`:

```python
prepare_headers(oauth_params, headers=None, realm=None) -> dict
prepare_form_encoded_body(oauth_params, body) -> list[tuple[str, str]]
prepare_request_uri_query(oauth_params, uri) -> str
```

Import signing primitives from `oauthlib.oauth1.rfc5849.signature`:

```python
base_string_uri(uri, host=None) -> str
collect_parameters(uri_query='', body=None, headers=None,
                   exclude_oauth_signature=True, with_realm=False) -> list
normalize_parameters(params) -> str
signature_base_string(http_method, base_str_uri,
                      normalized_encoded_request_parameters) -> str
sign_hmac_sha1(base_string, client_secret, resource_owner_secret) -> str
sign_hmac_sha256(base_string, client_secret, resource_owner_secret) -> str
sign_plaintext(client_secret, resource_owner_secret) -> str
```

OAuth1 encoding is RFC-compatible: secrets form the signing key, parameters
are percent-encoded and sorted for normalization, and an OAuth signature is
excluded from collected parameters by default. Authorization headers use the
`OAuth` scheme and percent-encoded values.

## OAuth 2.0 RFC 6749 and RFC 8628

Import utility functions from `oauthlib.oauth2.rfc6749.utils`:

```python
list_to_scope(scope) -> str
scope_to_list(scope) -> list[str]
params_from_uri(uri) -> dict
host_from_uri(uri) -> str
escape(value) -> str
is_secure_transport(uri) -> bool
```

Import request functions from `oauthlib.oauth2.rfc6749.parameters`:

```python
prepare_grant_uri(uri, client_id, response_type, redirect_uri=None,
                  scope=None, state=None, code_challenge=None,
                  code_challenge_method='plain', **kwargs) -> str
prepare_token_request(grant_type, body='', include_client_id=True,
                      code_verifier=None, **kwargs) -> tuple[str, str, dict]
prepare_token_revocation_request(url, token, token_type_hint='access_token',
                                 body='', **kwargs) -> tuple[str, str, dict]
parse_authorization_code_response(uri, state=None) -> dict
parse_implicit_response(uri, state=None, scope=None) -> dict
parse_token_response(body, scope=None) -> dict
parse_expires(params) -> dict
```

The parser functions return dictionaries and raise the package's OAuth2
errors for malformed or unsuccessful responses. Scopes preserve their OAuth2
space-separated convention. `prepare_grant_uri` and token helpers preserve
existing parameters and add supplied values in the documented encoding.

`OAuth2Token(params, old_scope=None)` is a dict subclass with scope comparison
helpers: `scope_changed()`, `old_scope()`, `old_scopes()`, `scope()`,
`scopes()`, `missing_scopes()`, and `additional_scopes()`. The bearer helpers
are `prepare_bearer_uri(token, uri)`, `prepare_bearer_headers(token,
headers=None)`, and `prepare_bearer_body(token, body='')`.

The client classes are stateful objects. Construct
`WebApplicationClient(client_id, code=None)`,
`MobileApplicationClient(client_id)`, `BackendApplicationClient(client_id)`,
`LegacyApplicationClient(client_id)`, or `DeviceClient(client_id)` from their
documented modules. Their request preparation methods delegate to the helpers
above and return `(uri, headers, body)` or `(uri, headers, body)`-compatible
tuples as documented by the class. Preserve client state when parsing token
and authorization responses. The verifier uses fixed client IDs, URLs, and
tokens; no remote request is sent.

# Implementation Notes

- Build an actual installable package with all package subdirectories and
  metadata; a single-file stub is insufficient.
- Preserve deterministic ordering, duplicate query parameters, percent
  encoding, and the distinction between query, body, headers, and fragments.
- Keep mutable request/client state isolated per instance. Do not share token,
  header, or parameter dictionaries across calls.
- Implement OAuth1 HMAC-SHA1, HMAC-SHA256, and PLAINTEXT locally with the
  standard library. The optional RSA and JWT extras are outside the hidden
  contract.
- Error classes and status behavior should remain inspectable. Do not replace
  protocol errors with silent defaults.
- The evaluator runs the candidate in bounded unprivileged child processes;
  the verifier is offline and does not import candidate code into its trusted
 process. Do not retrieve OAuthLib's reference source at runtime.

# Examples

```python
from oauthlib.common import urlencode, urldecode
encoded = urlencode([('scope', 'read write'), ('scope', 'write')])
urldecode(encoded)
```

```python
from oauthlib.oauth1.rfc5849.signature import sign_hmac_sha256
sign_hmac_sha256('base', 'client-secret', 'owner-secret')
```

```python
from oauthlib.oauth2.rfc6749.parameters import prepare_grant_uri
prepare_grant_uri('https://client.test/authorize', 'client', 'code', scope=['read'])
```

# Error Handling and Boundary Conditions

- Preserve malformed percent-escape, invalid URI, insecure transport, and
  OAuth protocol error classes rather than silently accepting bad input.
- Duplicate parameter order and percent encoding are significant to OAuth 1.0
  normalization.
- Client and token objects must isolate mutable state between instances and
  calls.
- RSA/JWT extras, signals, live services, credentials, subprocesses, and
  network access are outside this local contract.
