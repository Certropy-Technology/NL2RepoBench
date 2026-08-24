#!/usr/bin/env python3
"""Run deterministic google-auth scenarios inside the candidate process.

The root grader only consumes the JSON report emitted here. This file is the
task-specific child adapter: it is the only verifier component allowed to
import the candidate package.
"""

from __future__ import annotations

import datetime
import json
import os
import sys

# Take the run nonce and the real stdout away from the candidate before any
# candidate module can be imported:
#   * the nonce is popped from the environment, so candidate code cannot read it
#     out of os.environ and stamp a forged report;
#   * fd 1 is replaced by stderr and the original stdout is kept as a private
#     duplicate, so anything the candidate prints during import cannot inject a
#     second report marker into the graded channel.
_NONCE = os.environ.pop("NL2REPO_REPORT_NONCE", "")
_REPORT_FD = os.dup(1)
os.dup2(2, 1)

# `python -I` ignores PYTHONPATH, so the trusted parent passes the candidate site
# and the candidate dependency site as argv. Insert them before any candidate
# import so the adapter resolves the candidate build rather than a stray copy.
for _entry in reversed(sys.argv[1:]):
    if _entry and _entry not in sys.path:
        sys.path.insert(0, _entry)

# The fixed denominator. Declared before any candidate import so an import or
# collection failure still yields exactly 32 leaves instead of a short report.
SCENARIO_IDS = (
    "pkg.version",
    "pkg.namespaces",
    "helpers.scopes_string",
    "helpers.string_scopes",
    "helpers.bytes_roundtrip",
    "helpers.bytes_errors",
    "helpers.base64_roundtrip",
    "helpers.query_update",
    "helpers.datetime",
    "credentials.anonymous_state",
    "credentials.anonymous_token_error",
    "oauth.properties",
    "oauth.header_and_copy",
    "oauth.factories",
    "oauth.handler_validation",
    "oauth.universe_refresh_error",
    "credentials.scope_helper",
    "service_account.properties",
    "service_account.copies",
    "service_account.assertion",
    "jwt.encode_decode",
    "jwt.header",
    "jwt.malformed",
    "jwt.unverified_payload",
    "api_key.apply",
    "api_key.empty",
    "downscoped.boundary_json",
    "downscoped.boundary_limits",
    "cache.lru",
    "cache.disabled",
    "transport.constants",
    "exceptions.hierarchy",
)


class FakeSigner:
    key_id = "fake-key"

    def sign(self, message: bytes) -> bytes:
        return b"deterministic-signature"


def _check(name: str, function) -> dict[str, object]:
    try:
        function()
    except Exception as exc:  # candidate behavior is recorded as a leaf failure
        return {
            "id": name,
            "status": "failed",
            "message": f"{type(exc).__name__}: {exc}",
        }
    return {"id": name, "status": "passed"}


def _scenarios():
    from google.auth import (
        _cache,
        _helpers,
        api_key,
        credentials,
        downscoped,
        exceptions,
        jwt,
        transport,
    )
    from google.oauth2 import credentials as oauth_credentials
    from google.oauth2 import service_account

    def pkg_version():
        from google.auth import version
        assert version.__version__ == "2.56.3"

    def pkg_namespaces():
        import google.auth
        import google.oauth2
        assert google.auth.__name__ == "google.auth"
        assert google.oauth2.__name__ == "google.oauth2"
        assert credentials.DEFAULT_UNIVERSE_DOMAIN == "googleapis.com"

    def scopes_string():
        assert _helpers.scopes_to_string(["scope:b", "scope:a"]) == "scope:b scope:a"

    def string_scopes():
        assert _helpers.string_to_scopes("scope:b scope:a") == ["scope:b", "scope:a"]
        assert _helpers.string_to_scopes("") == []

    def bytes_roundtrip():
        assert _helpers.to_bytes("caf\u00e9") == b"caf\xc3\xa9"
        assert _helpers.from_bytes(b"caf\xc3\xa9") == "caf\u00e9"
        assert _helpers.to_bytes(b"same") == b"same"

    def bytes_errors():
        try:
            _helpers.to_bytes(3)
        except exceptions.InvalidValue:
            pass
        else:
            raise AssertionError("to_bytes accepted an integer")
        try:
            _helpers.from_bytes(3)
        except exceptions.InvalidValue:
            pass
        else:
            raise AssertionError("from_bytes accepted an integer")

    def base64_roundtrip():
        encoded = _helpers.unpadded_urlsafe_b64encode(b"hello?")
        assert encoded == b"aGVsbG8_"
        assert _helpers.padded_urlsafe_b64decode(encoded) == b"hello?"

    def query_update():
        result = _helpers.update_query(
            "https://example.test/path?a=1&remove=old",
            {"a": "2", "b": "hello world"},
            remove=["remove"],
        )
        assert result == "https://example.test/path?a=2&b=hello+world"

    def datetime_helpers():
        value = datetime.datetime(1970, 1, 1, 0, 0, 2)
        assert _helpers.datetime_to_secs(value) == 2
        assert _helpers.utcfromtimestamp(2) == value

    def anonymous_state():
        anon = credentials.AnonymousCredentials()
        assert anon.valid is True and anon.expired is False
        headers = {"x-test": "keep"}
        anon.apply(headers)
        assert headers == {"x-test": "keep"}

    def anonymous_token_error():
        try:
            credentials.AnonymousCredentials().apply({}, token="bad")
        except exceptions.InvalidValue:
            return
        raise AssertionError("anonymous credentials accepted a token")

    def oauth_properties():
        cred = oauth_credentials.Credentials(
            "access",
            refresh_token="refresh",
            id_token="id",
            token_uri="https://token.test",
            client_id="client",
            client_secret="secret",
            scopes=["one"],
            quota_project_id="quota",
            account="user@example.test",
        )
        assert cred.token == "access"
        assert cred.refresh_token == "refresh"
        assert cred.id_token == "id"
        assert cred.token_uri == "https://token.test"
        assert cred.client_id == "client"
        assert cred.client_secret == "secret"
        assert cred.scopes == ["one"]
        assert cred.account == "user@example.test"
        assert cred.requires_scopes is False

    def oauth_header_and_copy():
        cred = oauth_credentials.Credentials("access", quota_project_id="quota")
        headers = {}
        cred.apply(headers)
        assert headers == {
            "authorization": "Bearer access",
            "x-goog-user-project": "quota",
        }
        copy = cred.with_quota_project("other")
        assert copy is not cred and copy.quota_project_id == "other"
        assert cred.quota_project_id == "quota"

    def oauth_factories():
        cred = oauth_credentials.Credentials("access")
        assert cred.with_token_uri("new").token_uri == "new"
        assert cred.with_account("new@example.test").account == "new@example.test"
        assert cred.with_universe_domain("example.test").universe_domain == "example.test"

    def oauth_handler_validation():
        try:
            oauth_credentials.Credentials("access", refresh_handler=object())
        except TypeError:
            return
        raise AssertionError("non-callable refresh handler accepted")

    def oauth_universe_refresh_error():
        cred = oauth_credentials.Credentials(
            None,
            refresh_token="refresh",
            token_uri="https://token.test",
            client_id="client",
            client_secret="secret",
            universe_domain="example.test",
        )
        try:
            cred.refresh(None)
        except exceptions.RefreshError:
            return
        raise AssertionError("non-default universe refresh did not fail")

    def oauth_scope_helper():
        cred = service_account.Credentials(
            FakeSigner(),
            "sa@example.test",
            "https://token.test",
            project_id="project",
        )
        scoped = credentials.with_scopes_if_required(cred, ["scope:a"])
        assert scoped is not cred and scoped.scopes == ["scope:a"]

    def service_account_properties():
        cred = service_account.Credentials(
            FakeSigner(),
            "sa@example.test",
            "https://token.test",
            project_id="project",
        )
        assert cred.service_account_email == "sa@example.test"
        assert cred.project_id == "project"
        assert cred.requires_scopes is True

    def service_account_copies():
        cred = service_account.Credentials(
            FakeSigner(), "sa@example.test", "https://token.test", scopes=["old"]
        )
        assert cred.with_scopes(["new"]).scopes == ["new"]
        assert cred.with_subject("user@example.test")._subject == "user@example.test"
        assert cred.with_claims({"region": "us"})._additional_claims == {"region": "us"}
        assert cred.with_quota_project("quota").quota_project_id == "quota"

    def service_account_assertion():
        cred = service_account.Credentials(
            FakeSigner(),
            "sa@example.test",
            "https://token.test",
            scopes=["scope:b", "scope:a"],
            additional_claims={"custom": "value"},
        )
        payload = jwt.decode(cred._make_authorization_grant_assertion(), verify=False)
        assert payload["iss"] == "sa@example.test"
        assert payload["aud"] == "https://oauth2.googleapis.com/token"
        assert payload["scope"] == "scope:b scope:a"
        assert payload["custom"] == "value"
        assert payload["exp"] - payload["iat"] == 3600

    def jwt_encode_decode():
        token = jwt.encode(FakeSigner(), {"sub": "subject", "n": 3})
        assert isinstance(token, bytes)
        assert jwt.decode(token, verify=False) == {"sub": "subject", "n": 3}

    def jwt_header():
        token = jwt.encode(FakeSigner(), {"sub": "subject"}, key_id="override")
        header = jwt.decode_header(token)
        assert header == {"alg": "RS256", "kid": "override", "typ": "JWT"}

    def jwt_malformed():
        try:
            jwt.decode("not-a-jwt", verify=False)
        except exceptions.MalformedError:
            return
        raise AssertionError("malformed JWT accepted")

    def jwt_unverified_payload():
        token = jwt.encode(FakeSigner(), {"aud": "wanted"})
        assert jwt.decode(token, verify=False, audience="other") == {"aud": "wanted"}

    def api_key_apply():
        cred = api_key.Credentials("key")
        headers = {}
        cred.before_request(None, "GET", "https://example.test", headers)
        assert headers == {"x-goog-api-key": "key"}
        assert cred.valid is True and cred.expired is False

    def api_key_empty():
        try:
            api_key.Credentials("")
        except exceptions.InvalidValue:
            return
        raise AssertionError("empty API key accepted")

    def boundary_json():
        condition = downscoped.AvailabilityCondition(
            "resource.name.startsWith('objects/a')", title="prefix"
        )
        rule = downscoped.AccessBoundaryRule(
            "//storage.googleapis.com/projects/_/buckets/demo",
            ["inRole:roles/storage.objectViewer"],
            condition,
        )
        boundary = downscoped.CredentialAccessBoundary([rule])
        assert boundary.rules == (rule,)
        assert boundary.to_json() == {
            "accessBoundary": {
                "accessBoundaryRules": [{
                    "availablePermissions": ["inRole:roles/storage.objectViewer"],
                    "availableResource": "//storage.googleapis.com/projects/_/buckets/demo",
                    "availabilityCondition": {
                        "expression": "resource.name.startsWith('objects/a')",
                        "title": "prefix",
                    },
                }]
            }
        }

    def boundary_limits():
        rule = downscoped.AccessBoundaryRule("resource", ["inRole:role"])
        try:
            downscoped.CredentialAccessBoundary([rule] * 11)
        except exceptions.InvalidValue:
            pass
        else:
            raise AssertionError("more than ten rules accepted")
        try:
            downscoped.AccessBoundaryRule("resource", ["role"])
        except exceptions.InvalidValue:
            return
        raise AssertionError("unprefixed permission accepted")

    def cache_lru():
        cache = _cache.LRUCache(2)
        cache["a"] = 1
        cache["b"] = 2
        assert cache["a"] == 1
        cache["c"] = 3
        assert "b" not in cache and list(cache) == ["a", "c"]
        cache.clear()
        assert len(cache) == 0

    def cache_disabled():
        cache = _cache.LRUCache(0)
        cache["a"] = 1
        assert cache.get("a") is None and len(cache) == 0

    def transport_constants():
        assert transport.DEFAULT_RETRYABLE_STATUS_CODES == (500, 503, 504, 408, 429)
        assert transport.DEFAULT_REFRESH_STATUS_CODES == (401,)
        assert transport.DEFAULT_MAX_REFRESH_ATTEMPTS == 2

    def exception_hierarchy():
        error = exceptions.MalformedError("bad", retryable=True)
        assert isinstance(error, exceptions.DefaultCredentialsError)
        assert error.retryable is True
        assert issubclass(exceptions.InvalidType, TypeError)

    return [
        ("pkg.version", pkg_version),
        ("pkg.namespaces", pkg_namespaces),
        ("helpers.scopes_string", scopes_string),
        ("helpers.string_scopes", string_scopes),
        ("helpers.bytes_roundtrip", bytes_roundtrip),
        ("helpers.bytes_errors", bytes_errors),
        ("helpers.base64_roundtrip", base64_roundtrip),
        ("helpers.query_update", query_update),
        ("helpers.datetime", datetime_helpers),
        ("credentials.anonymous_state", anonymous_state),
        ("credentials.anonymous_token_error", anonymous_token_error),
        ("oauth.properties", oauth_properties),
        ("oauth.header_and_copy", oauth_header_and_copy),
        ("oauth.factories", oauth_factories),
        ("oauth.handler_validation", oauth_handler_validation),
        ("oauth.universe_refresh_error", oauth_universe_refresh_error),
        ("credentials.scope_helper", oauth_scope_helper),
        ("service_account.properties", service_account_properties),
        ("service_account.copies", service_account_copies),
        ("service_account.assertion", service_account_assertion),
        ("jwt.encode_decode", jwt_encode_decode),
        ("jwt.header", jwt_header),
        ("jwt.malformed", jwt_malformed),
        ("jwt.unverified_payload", jwt_unverified_payload),
        ("api_key.apply", api_key_apply),
        ("api_key.empty", api_key_empty),
        ("downscoped.boundary_json", boundary_json),
        ("downscoped.boundary_limits", boundary_limits),
        ("cache.lru", cache_lru),
        ("cache.disabled", cache_disabled),
        ("transport.constants", transport_constants),
        ("exceptions.hierarchy", exception_hierarchy),
    ]


def main() -> int:
    try:
        cases = _scenarios()
        if tuple(name for name, _ in cases) != SCENARIO_IDS:
            raise AssertionError("adapter scenario list drifted from SCENARIO_IDS")
        leaves = [_check(name, function) for name, function in cases]
    except BaseException as exc:  # candidate import/collection failure
        leaves = [
            {
                "id": name,
                "status": "failed",
                "message": f"adapter-collection-failed: {type(exc).__name__}: {exc}"[:2000],
            }
            for name in SCENARIO_IDS
        ]
    payload = {
        "schema_version": "1.0",
        "nonce": _NONCE,
        "leaves": leaves,
    }
    # Written to the private stdout duplicate that the candidate never sees.
    sys.stdout.flush()
    sys.stderr.flush()
    os.write(
        _REPORT_FD,
        ("NL2REPO_REPORT=" + json.dumps(payload, sort_keys=True) + "\n").encode("utf-8"),
    )
    return 1 if any(leaf["status"] == "failed" for leaf in leaves) else 0


if __name__ == "__main__":
    raise SystemExit(main())
