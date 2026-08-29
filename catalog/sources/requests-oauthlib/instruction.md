# Build `requests-oauthlib`

Create a complete, installable Python package named `requests-oauthlib` from an empty workspace. It must provide deterministic, offline OAuth request preparation and local token-processing behavior compatible with requests-oauthlib 2.0.0. Do not copy upstream source or tests into the workspace.

## Project Description

Implement the Python package `requests_oauthlib` for CPython 3.12 on Linux. It adapts the installed `requests` and `oauthlib` libraries with OAuth 1 request signing, OAuth 2 session helpers, local token parsing, and provider compliance hooks. No authorization server, browser, credential service, or protected-resource endpoint exists.

## Supports

- Source-only installation with `pip install .`, without a `.git` directory or downloading build dependencies.
- CPython 3.12 on Linux amd64. The environment provides `requests 2.31.0`, `oauthlib 3.3.0` with signed-token support, and setuptools.
- Offline creation and mutation of requests, URLs, headers, bodies, token dictionaries, and response-like values. Runtime code must not invoke `git`, `curl`, `wget`, browser automation, or a network endpoint.
- Public modules `requests_oauthlib`, `oauth1_auth`, `oauth1_session`, `oauth2_auth`, `oauth2_session`, and the documented `compliance_fixes` modules.

## API Usage Guide

### Package exports

`requests_oauthlib.__version__` is `"2.0.0"`. The package exports `OAuth1`, `OAuth1Session`, `OAuth2`, `OAuth2Session`, and `TokenUpdated`.

### OAuth 1

`OAuth1(client_key, client_secret=None, resource_owner_key=None, resource_owner_secret=None, callback_uri=None, signature_method=..., signature_type=..., rsa_key=None, verifier=None, decoding="utf-8", client_class=None, force_include_body=False, **kwargs)` is a `requests.auth.AuthBase` implementation. Calling it with a prepared HTTPS request signs it through oauthlib and updates the Authorization header, request URL, or form body according to `signature_type`. Form-encoded bodies are included by default; `force_include_body=True` also includes other bodies.

`OAuth1Session(...)` has the corresponding OAuth 1 constructor arguments and inherits requests session behavior. Its `token` property is a dictionary with present `oauth_token`, `oauth_token_secret`, and `oauth_verifier` fields. `authorized` is true only when credentials required by the signature method are present. `authorization_url(url, request_token=None, **kwargs)` returns a URL with the request token and optional parameters. `parse_authorization_response(url)` parses and stores the redirect query, returning the token dictionary; missing `oauth_token` raises `TokenMissing`. `fetch_request_token(url, realm=None, **request_kwargs)` and `fetch_access_token(url, verifier=None, **request_kwargs)` parse an OAuth endpoint response supplied through normal requests session behavior. A failing endpoint response raises `TokenRequestDenied`; calling the latter without a verifier raises `VerifierMissing`.

### OAuth 2

`OAuth2(client_id=None, client=None, token=None)` adds a token to a prepared HTTPS request and raises oauthlib's insecure-transport error for a non-HTTPS URL.

`OAuth2Session(client_id=None, client=None, auto_refresh_url=None, auto_refresh_kwargs=None, scope=None, redirect_uri=None, token=None, state=None, token_updater=None, pkce=None, **kwargs)` manages an oauthlib client. `scope`, `client_id`, `token`, `access_token`, and `authorized` are observable properties. `authorization_url(url, state=None, **kwargs)` returns `(url, state)`, carrying configured redirect URI and scope. `pkce` accepts only `"S256"`, `"plain"`, or `None`; a PKCE authorization URL includes a challenge. `token_from_fragment(authorization_response)` returns and stores the parsed token. `fetch_token(...)` and `refresh_token(...)` make the normal requests call only when invoked, parse the local response, and require HTTPS. `request(method, url, ..., withhold_token=False, ...)` adds a valid token to a HTTPS protected request unless withholding is requested. Unsupported compliance hook names raise `ValueError`; valid hooks are registered and run in their documented request/response phase.

### Compliance fixes

The following functions accept an `OAuth2Session`, register their documented hook(s), and return that same session: `facebook_compliance_fix`, `fitbit_compliance_fix`, `mailchimp_compliance_fix`, `weibo_compliance_fix`, `slack_compliance_fix`, `instagram_compliance_fix`, `ebay_compliance_fix`, and `plentymarkets_compliance_fix`. They only transform local OAuth response data or outgoing request parameters; they do not contact the named provider.

## Implementation Notes

Preserve requests and oauthlib exception identity rather than replacing typed errors with generic exceptions. Observable token dictionaries and URL query parameters must use standard URL encoding. OAuth signing can use oauthlib nonce and timestamp generation; callers should rely on the presence and shape of OAuth parameters rather than a fixed signature string. Network-capable methods must remain lazy until a caller supplies a request implementation.
