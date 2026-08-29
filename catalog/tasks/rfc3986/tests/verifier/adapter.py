from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any


def type_name(exc: BaseException) -> str:
    return f"{type(exc).__module__}.{type(exc).__qualname__}"


def exercise(scenario: str) -> Any:
    from rfc3986 import IRIReference, URIReference, __version__, iri_reference, is_valid_uri, normalize_uri, uri_reference, urlparse
    from rfc3986 import builder, exceptions, misc, normalizers, validators
    from rfc3986.parseresult import ParseResult, ParseResultBytes

    if scenario == "api/components":
        ref = uri_reference("http://user:pass@example.com:8080/a/b?x=1#frag")
        return [ref.scheme, ref.authority, ref.path, ref.query, ref.fragment, ref.authority_info()]
    if scenario == "api/unsplit":
        return uri_reference("http://example.com/a%2fb?x=%3a#f").unsplit()
    if scenario == "api/normalize":
        return normalize_uri("HTTP://EXAMPLE.COM/a/../b/%7e?q=%3a")
    if scenario == "api/valid":
        return [is_valid_uri("https://example.com/path", require_scheme=True), is_valid_uri("not a uri")]
    if scenario == "uri/absolute":
        return [uri_reference("https://example.com").is_absolute(), uri_reference("../x").is_absolute()]
    if scenario == "uri/resolve":
        return uri_reference("../x?y=1").resolve_with("http://example.com/a/b").unsplit()
    if scenario == "uri/copy":
        return uri_reference("http://example.com/a").copy_with(path="/b", fragment="f").unsplit()
    if scenario == "uri/userinfo":
        ref = uri_reference("http://user:pass@example.com:8080/a")
        return [ref.userinfo, ref.host, ref.port]
    if scenario == "iri/parts":
        ref = iri_reference("https://例え.テスト/パス?q=値#部分")
        return [ref.authority, ref.path, ref.query, ref.fragment]
    if scenario == "iri/encode":
        return iri_reference("https://例え.テスト/パス?q=値#部分").encode().unsplit()
    if scenario == "parse/urlparse":
        return list(urlparse("http://user:pass@example.com:8080/a?x=1#f"))
    if scenario == "parse/shims":
        result = urlparse("http://example.com/a?x=1")
        return [result.hostname, result.netloc, result.params, result.geturl()]
    if scenario == "parse/copy":
        return urlparse("http://example.com/a?x=1").copy_with(path="/b", query="y=2").unsplit()
    if scenario == "parse/encode":
        result = urlparse("http://example.com/a?x=1").encode()
        return [type(result).__name__, result.unsplit().decode("ascii")]
    if scenario == "parse/from-parts":
        return ParseResult.from_parts("https", "u", "example.com", "443", "/x", "a=1", "f").unsplit()
    if scenario == "builder/chain":
        return builder.URIBuilder().add_scheme("HTTPS").add_host("Example.COM").add_path("a/../b").add_query_from({"q": "a b"}).add_fragment("Top").geturl()
    if scenario == "builder/credentials":
        return builder.URIBuilder().add_credentials("u", "p@ss").add_host("example.com").finalize().unsplit()
    if scenario == "builder/extend":
        return builder.URIBuilder(path="/a").extend_path("/b").extend_query_with({"x": "1"}).geturl()
    if scenario == "normalizers/percent":
        return normalizers.normalize_percent_characters("%3a%AF%zz")
    if scenario == "normalizers/host":
        return normalizers.normalize_host("EXAMPLE.COM")
    if scenario == "normalizers/ipv6-zone":
        return normalizers.normalize_host("[FE80::1%eth0]")
    if scenario == "normalizers/path":
        return normalizers.normalize_path("/a/./b/../c")
    if scenario == "normalizers/encoding":
        return normalizers.encode_component("café path", "utf-8")
    if scenario == "misc/merge":
        return misc.merge_paths(uri_reference("http://e/a/b"), "c")
    if scenario == "validator/ok":
        return validators.Validator().require_presence_of("scheme", "host").allow_schemes("HTTP", "https").allow_hosts("example.com").validate(uri_reference("https://example.com/x"))
    if scenario == "validator/missing":
        try:
            validators.Validator().require_presence_of("host").validate(uri_reference("/x"))
        except Exception as exc:
            return type_name(exc)
    if scenario == "validator/unpermitted":
        try:
            validators.Validator().allow_schemes("https").validate(uri_reference("http://example.com"))
        except Exception as exc:
            return type_name(exc)
    if scenario == "validator/password":
        try:
            validators.Validator().forbid_use_of_password().validate(uri_reference("http://u:p@example.com"))
        except Exception as exc:
            return type_name(exc)
    if scenario == "validator/ipv4":
        return [validators.valid_ipv4_host_address("192.168.1.1"), validators.valid_ipv4_host_address("999.1.1.1")]
    if scenario == "exceptions/messages":
        return [str(exceptions.InvalidPort("abc")), str(exceptions.InvalidAuthority(b"bad"))]
    if scenario == "bytes/reference":
        ref = URIReference.from_string(b"http://example.com/a")
        result = ParseResultBytes.from_string(b"http://example.com")
        return [type(ref.path).__name__, ref.unsplit(), type(result.scheme).__name__, result.unsplit().decode("ascii")]
    if scenario == "uri/query-empty":
        return uri_reference("http://example.com/a?").unsplit()
    if scenario == "uri/fragment-empty":
        return uri_reference("http://example.com/a#").unsplit()
    if scenario == "uri/normalized-equality":
        return uri_reference("HTTP://EXAMPLE.COM/a/../b").normalized_equality(uri_reference("http://example.com/b"))
    if scenario == "uri/authority-invalid":
        try:
            uri_reference("http://[bad/a").authority_info()
        except Exception as exc:
            return type_name(exc)
    if scenario == "validator/component":
        return [bool(validators.scheme_is_valid("https", True)), bool(validators.path_is_valid("/a", True)), bool(validators.query_is_valid("a=1", True))]
    if scenario == "builder/port-boundary":
        return [builder.URIBuilder().add_port(0).port, builder.URIBuilder().add_port(65535).port]
    if scenario == "api/reexports":
        return [__version__, URIReference.__name__, IRIReference.__name__, callable(uri_reference), callable(urlparse)]
    raise ValueError(f"unknown scenario: {scenario}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--dependency-site", required=True)
    parser.add_argument("--scenario", required=True)
    args = parser.parse_args()
    if os.path.realpath(args.candidate_site) != "/tmp/candidate-site":
        raise ValueError("candidate site is unavailable")
    if os.path.realpath(args.dependency_site) != "/opt/candidate-dependencies/site":
        raise ValueError("dependency site is unavailable")
    sys.path.insert(0, args.dependency_site)
    sys.path.insert(0, args.candidate_site)
    try:
        value = exercise(args.scenario)
        print(json.dumps({"ok": True, "value": value}, sort_keys=True, default=lambda v: v.decode("ascii")))
    except BaseException as exc:
        print(json.dumps({"ok": False, "exception_type": type_name(exc), "exception_message": str(exc)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
