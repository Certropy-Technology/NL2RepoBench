# MSAL Traceability

The public contract is a deterministic offline adaptation of the frozen
revision, not a claim that the full Azure integration suite is runnable without
credentials or external services.

| Leaf group | Public contract section | Upstream evidence |
| --- | --- | --- |
| exports and packaging | Supports | `msal/__init__.py`, `msal/sku.py`, `setup.cfg` |
| authority and OIDC | API Usage Guide: Authority helpers; OAuth/OIDC | `msal/authority.py`, `msal/oauth2cli/oidc.py`, `tests/test_authority.py`, `tests/test_oidc.py` |
| OAuth request construction | API Usage Guide: OAuth/OIDC request | `msal/oauth2cli/oauth2.py`, `tests/test_authcode.py`, `tests/test_application.py` |
| token cache and claims | API Usage Guide: Token cache | `msal/token_cache.py`, `tests/test_token_cache.py` |
| response throttling | API Usage Guide: Response and throttling | `msal/throttled_http_client.py`, `msal/oauth2cli/http.py`, `tests/test_throttled_http_client.py` |
| auth scheme and XML | API Usage Guide: Response, throttling, authentication, XML | `msal/auth_scheme.py`, `msal/wstrust_request.py`, `tests/test_wstrust.py` |

The private adapter does not import candidate modules in the trusted pytest
process. Each case is sent as JSON to a candidate-owned subprocess and only
JSON-safe observations return to the root verifier. The adapter's expected
values are behavioral assertions derived from the frozen implementation; it
does not expose upstream source bytes to the model agent.
