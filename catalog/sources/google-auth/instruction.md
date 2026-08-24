# Project Description

Build a clean-room Python package named `google-auth` that provides the
offline, deterministic core of Google's authentication library. The package
must install from an empty workspace and expose the `google.auth` and
`google.oauth2` namespaces. It is used by client libraries to represent
credentials, construct OAuth/JWT assertions, add authentication headers, and
describe downscoped access boundaries.

This task evaluates the deterministic library contract only. It does not
require real Google accounts, metadata servers, AWS credentials, browser
flows, or network access. Do not contact any service during tests.

# Supports

- Python 3.12 on a Linux system.
- A normal install with `pip install .` or an equivalent PEP 517/setuptools
  install. A legacy `setup.py` is acceptable, but the distribution metadata
  must identify the distribution as `google-auth` and report version `2.56.3`.
- Runtime dependencies may be standard library modules plus
  `cryptography` and `pyasn1-modules`. Keep imports usable when optional
  transport packages are absent; the scored core must not require requests,
  aiohttp, grpcio, Flask, or any cloud SDK.
- The import packages `google.auth`, `google.auth.crypt`,
  `google.auth.transport`, `google.auth.downscoped`, `google.auth.api_key`,
  `google.auth._cache`, `google.oauth2`, `google.oauth2.credentials`,
  `google.oauth2.service_account`, and `google.auth.jwt`.

# API Usage Guide

## Common helpers

Implement these functions in `google.auth._helpers`:

- `to_bytes(value, encoding="utf-8")` converts `str` to UTF-8 bytes and
  preserves bytes. Other values raise `google.auth.exceptions.InvalidValue`.
- `from_bytes(value)` converts bytes to text and preserves text; other values
  raise `InvalidValue`.
- `scopes_to_string(scopes)` joins scopes with one ASCII space.
- `string_to_scopes(scopes)` splits a space-separated string and returns an
  empty list for an empty or false value.
- `unpadded_urlsafe_b64encode(value)` returns URL-safe base64 bytes with
  trailing `=` removed. `padded_urlsafe_b64decode(value)` accepts the
  unpadded form and restores padding.
- `datetime_to_secs(value)` returns UTC Unix seconds as an integer,
  `utcnow()` returns a naive UTC datetime, and `utcfromtimestamp(value)`
  returns a naive UTC datetime.
- `update_query(url, params, remove=None)` replaces existing query keys,
  appends new keys, preserves the URL components, and removes keys listed in
  `remove`.

## Credential base classes

In `google.auth.credentials`, provide `Credentials` with the documented
properties `token`, `expiry`, `expired`, `valid`, `token_state`,
`quota_project_id`, and `universe_domain`. `TokenState` has the values
`FRESH`, `STALE`, and `INVALID`. A token with no expiry is fresh; an expired
token is invalid; a token inside the refresh threshold is stale.

`Credentials.apply(headers, token=None)` adds a bearer `Authorization` header
using the supplied token or the current token, and adds
`x-goog-user-project` when a quota project is set. `before_request(request,
method, url, headers)` refreshes invalid credentials and then applies them.
The abstract `refresh(request)` method must raise `NotImplementedError` when
not implemented.

Provide `AnonymousCredentials`, `Scoped`, `ReadOnlyScoped`, `Signing`,
`CredentialsWithQuotaProject`, `CredentialsWithTokenUri`, and
`CredentialsWithUniverseDomain` with the copy/factory behavior exercised by
the tests. `with_scopes_if_required(credentials, scopes, default_scopes=None)`
returns a scoped copy only when `requires_scopes` is true.

## OAuth 2.0 credentials

`google.oauth2.credentials.Credentials` accepts the full constructor:

```text
Credentials(token, refresh_token=None, id_token=None, token_uri=None,
            client_id=None, client_secret=None, scopes=None,
            default_scopes=None, quota_project_id=None, expiry=None,
            rapt_token=None, refresh_handler=None,
            enable_reauth_refresh=False, granted_scopes=None,
            trust_boundary=None, universe_domain="googleapis.com",
            account=None)
```

Expose read-only properties for these values, including `refresh_token`,
`id_token`, `token_uri`, `client_id`, `client_secret`, `scopes`,
`granted_scopes`, `rapt_token`, `account`, `refresh_handler`, and
`requires_scopes` (false). `refresh_handler` must be callable or `None`.
`with_quota_project`, `with_token_uri`, `with_account`, and
`with_universe_domain` return independent copies without changing the
original. A non-default universe domain cannot use the normal OAuth refresh
flow and must raise `google.auth.exceptions.RefreshError` before any network
request. `get_cred_info()` returns `None` unless a credential file path is
known.

## Service-account credentials

`google.oauth2.service_account.Credentials` stores a signer, service-account
email, token URI, scopes/default scopes, subject, project ID, quota project,
additional claims, `always_use_jwt_access`, and universe domain. Provide:

- `from_service_account_info(info, **kwargs)` and
  `from_service_account_file(filename, **kwargs)`;
- properties `service_account_email`, `project_id`, and `requires_scopes`;
- independent copies from `with_scopes`, `with_subject`, `with_claims`,
  `with_quota_project`, `with_token_uri`, `with_universe_domain`, and
  `with_always_use_jwt_access`;
- `_make_authorization_grant_assertion()` returning a signed JWT assertion
  with issuer equal to the service-account email, audience equal to
  `https://oauth2.googleapis.com/token`, a one-hour `iat`/`exp` window, and
  a space-joined scope claim. Additional claims override same-named defaults.

## JWT and signing

`google.auth.jwt.encode(signer, payload, header=None, key_id=None)` returns
compact JWT bytes. It always includes `typ: JWT`, defaults RSA signers to
`alg: RS256`, uses the explicit key ID over the signer's key ID, and signs the
header/payload segments. `decode_header(token)` parses the header without
verification. `decode(token, certs=None, verify=True, audience=None,
clock_skew_in_seconds=0)` validates the compact shape and, when `verify=False`,
returns the JSON payload without requiring certificates. With verification
enabled, it validates the signature, time claims, and optional audience.
Malformed tokens raise `google.auth.exceptions.MalformedError`; an unsupported
algorithm or wrong audience raises `InvalidValue`.

`google.auth.crypt.base.Signer` and `Verifier` are abstract interfaces. The
RSA implementations must expose `sign`, `verify`, and `key_id`, and
`google.auth.crypt.verify_signature(message, signature, certs, verifier_cls)`
returns whether any supplied certificate verifies the signature.

## API-key, downscoping, cache, and transport surfaces

- `google.auth.api_key.Credentials(token)` rejects an empty token with
  `InvalidValue`, reports `valid=True` and `expired=False`, and writes
  `x-goog-api-key` in `apply`/`before_request`.
- `google.auth.downscoped.AccessBoundaryRule(resource, available_permissions,
  availability_condition=None)` serializes to the documented
  `availableResource`, `availablePermissions`, and optional `availabilityCondition`
  keys. `CredentialAccessBoundary` accepts at most ten rules, validates rule
  types, exposes an immutable tuple through `rules`, and serializes with
  `to_json()` to `{"accessBoundary": {"accessBoundaryRules": [...]}}`.
- `google.auth._cache.LRUCache(maxsize)` evicts the least-recently-used key,
  refreshes recency on get/index, supports `clear`, and treats non-positive
  sizes as a disabled cache.
- `google.auth.transport.Response` and `Request` are abstract interfaces.
  Export the retry status constants and preserve their values: retryable
  statuses are 500, 503, 504, 408, and 429; refresh status is 401; the
  default maximum refresh attempts is 2.

# Implementation Notes

- Keep the two namespaces as real packages with the expected re-exports and
  include `py.typed` markers.
- Preserve input ordering and deterministic JSON/URL serialization. Do not
  use wall-clock values in assertions except for the service-account JWT
  window, which is checked as a one-hour interval.
- Exceptions belong under `google.auth.exceptions`, including
  `InvalidValue`, `InvalidType`, `MalformedError`, `RefreshError`, and
  `TransportError`.
- Optional network transports may be stubs that raise a clear transport error
  when their optional dependency is unavailable. They must not make import of
  the deterministic modules fail.
- Do not include tests, verifier code, generated reward files, or source
  archives in the candidate package. The evaluator supplies its own separate
  verifier and imports your package directly, so you do not need to write any
  test harness, reporting bridge, or grading code.
- The evaluator installs the workspace with an offline
  `pip install --no-index <workspace>` against a preloaded wheelhouse that
  provides `setuptools`, `wheel`, `cryptography`, and `pyasn1-modules`. The
  build must therefore succeed without network access and must not require a
  build dependency outside that set.
