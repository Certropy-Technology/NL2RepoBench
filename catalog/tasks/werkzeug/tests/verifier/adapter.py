from __future__ import annotations

import argparse
import base64
import io
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any


def typename(exc: BaseException) -> str:
    return f"{type(exc).__module__}.{type(exc).__qualname__}"


def run(scenario: str) -> Any:
    from werkzeug.datastructures import (
        Accept,
        Authorization,
        ETags,
        FileStorage,
        Headers,
        ImmutableMultiDict,
        MIMEAccept,
        MultiDict,
        TypeConversionDict,
    )
    from werkzeug.http import (
        dump_cookie,
        dump_header,
        dump_options_header,
        generate_etag,
        http_date,
        parse_cookie,
        parse_date,
        parse_dict_header,
        parse_list_header,
        parse_options_header,
        quote_etag,
        unquote_etag,
    )
    from werkzeug.routing import Map, Rule
    from werkzeug.security import check_password_hash, generate_password_hash, safe_join
    from werkzeug.sansio.request import Request as SansioRequest
    from werkzeug.sansio.response import Response as SansioResponse
    from werkzeug.test import Client, EnvironBuilder, create_environ
    from werkzeug.urls import iri_to_uri, uri_to_iri
    from werkzeug.wrappers import Request, Response
    from werkzeug.wsgi import LimitedStream, get_current_url, get_host

    if scenario == "multidict":
        m = MultiDict([("a", "1"), ("a", "2"), ("b", "x")])
        return [m["a"], m.getlist("a"), m.to_dict(flat=False), list(m.items(multi=True))]
    if scenario == "multidict_convert":
        m = MultiDict([("n", "2"), ("n", "bad"), ("n", "3")])
        return [m.getlist("n", type=int), m.get("missing", "d"), m.setlist("n", ["4", "5"]), m.getlist("n")]
    if scenario == "immutable":
        m = ImmutableMultiDict([("a", "1"), ("a", "2")])
        try:
            m.add("a", "3")  # type: ignore[attr-defined]
        except Exception as exc:
            return [m.getlist("a"), typename(exc), type(m.copy()).__name__]
        return None
    if scenario == "type_conversion":
        d = TypeConversionDict({"n": "4", "bad": "x"})
        return [d.get("n", type=int), d.get("bad", 9, type=int), d.get("none", 7, type=int)]
    if scenario == "headers":
        h = Headers([("Content-Type", "text/plain"), ("X-Test", "a")])
        h.add("x-test", "b")
        h["CONTENT-TYPE"] = "text/html"
        return [h["content-type"], h.getlist("X-Test"), h.to_wsgi_list()]
    if scenario == "accept":
        a = Accept.from_header("text/plain;q=0.5, text/html, */*;q=0.1")
        return [a.best_match(["application/json", "text/plain"]), a.quality("text/html"), list(a.values())]
    if scenario == "mime_accept":
        a = MIMEAccept.from_header("text/*;q=0.8, application/json;q=1")
        return [a.best_match(["text/html", "application/json"]), a.accept_html, a.accept_json]
    if scenario == "etags":
        e = ETags.from_header('"abc", W/"weak", *')
        return [e.contains("abc"), e.contains_weak("weak"), e.is_weak("weak"), e.to_header(), sorted(e.as_set(include_weak=True))]
    if scenario == "authorization":
        token = base64.b64encode(b"alice:secret").decode()
        a = Authorization.from_header(f"Basic {token}")
        return [a.type, a.username, a.password, a.to_header()]
    if scenario == "http_headers":
        return [parse_list_header('a, "b,c", d'), dump_header(["a", "b,c"]), parse_dict_header("a=1; b=two"), dump_options_header("text/plain", {"charset": "utf-8", "x": "a b"})]
    if scenario == "options":
        return list(parse_options_header('form-data; name="field"; filename="a.txt"'))
    if scenario == "etag":
        return [quote_etag("abc"), quote_etag("abc", weak=True), list(unquote_etag('W/"abc"')), generate_etag(b"abc")]
    if scenario == "date":
        value = datetime(2020, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
        return [http_date(value), parse_date(http_date(value)).isoformat()]
    if scenario == "cookie":
        header = dump_cookie("session", "abc", path="/", httponly=True, samesite="Lax")
        return [header, parse_cookie(header).get("session")]
    if scenario == "urls":
        return [iri_to_uri("https://例え.テスト/路径?q=雪"), uri_to_iri("https://xn--r8jz45g.xn--zckzah/%E8%B7%AF")]
    if scenario == "safe_join":
        return [safe_join("/srv/files", "a", "b.txt"), safe_join("/srv/files", "../secret"), safe_join("/srv/files", "/etc/passwd")]
    if scenario == "password":
        encoded = generate_password_hash("secret", method="pbkdf2", salt_length=8)
        return [encoded.startswith("pbkdf2:"), check_password_hash(encoded, "secret"), check_password_hash(encoded, "wrong")]
    if scenario == "wsgi_host":
        env = {"wsgi.url_scheme": "https", "SERVER_NAME": "example.test", "SERVER_PORT": "443", "HTTP_HOST": "example.test", "PATH_INFO": "/x", "SCRIPT_NAME": "", "QUERY_STRING": "a=1"}
        return [get_host(env), get_current_url(env)]
    if scenario == "limited_stream":
        stream = LimitedStream(io.BytesIO(b"abcdef"), 4)
        return [stream.read(2).decode(), stream.read().decode(), stream.tell(), stream.exhaust()]
    if scenario == "limited_stream_disconnect":
        stream = LimitedStream(io.BytesIO(b"ab"), 4, is_max=True)
        try:
            stream.read()
        except Exception as exc:
            return typename(exc)
        return None
    if scenario == "sansio_request":
        req = SansioRequest(method="POST", scheme="https", server=("example.test", 443), root_path="", remote_addr=None, path="/a", query_string="x=1", headers={"Content-Type": "application/json", "Host": "example.test"})
        return [req.url, req.base_url, req.host, req.is_secure, req.is_json]
    if scenario == "sansio_response":
        res = SansioResponse("201 Created", {"Content-Type": "application/json"})
        res.set_cookie("sid", "abc")
        return [res.status_code, res.status, res.mimetype, res.is_json, res.headers.get("Set-Cookie", "").startswith("sid=abc")]
    if scenario == "response":
        res = Response("hello", status=201, headers={"X-Test": "yes"})
        return [res.status_code, res.get_data(as_text=True), res.headers["X-Test"]]
    if scenario == "request_values":
        req = Request.from_values("/search?q=hello", method="POST", data={"name": "Alice"})
        return [req.path, req.args["q"], req.form["name"]]
    if scenario == "client":
        def app(environ, start_response):
            request = Request(environ)
            return Response(f"{request.method}:{request.args.get('x')}")(environ, start_response)
        response = Client(app).get("/hello?x=1")
        return [response.status_code, response.data.decode(), response.text]
    if scenario == "client_cookie":
        def app(environ, start_response):
            request = Request(environ)
            if request.cookies.get("sid"):
                return Response("seen")(environ, start_response)
            return Response("set", headers={"Set-Cookie": "sid=abc; Path=/"})(environ, start_response)
        client = Client(app)
        first, second = client.get("/"), client.get("/")
        return [first.data.decode(), second.data.decode()]
    if scenario == "routing_match":
        adapter = Map([Rule("/user/<int:id>", endpoint="user")]).bind("example.test")
        endpoint, values = adapter.match("/user/42")
        return [endpoint, values]
    if scenario == "routing_build":
        adapter = Map([Rule("/user/<int:id>", endpoint="user")]).bind("example.test")
        return [adapter.build("user", {"id": 42}), adapter.build("user", {"id": 42}, force_external=True)]
    if scenario == "environ":
        env = create_environ("/hello?x=1", method="POST", data={"name": "Alice"}, headers={"X-Test": "yes"})
        return [env["REQUEST_METHOD"], env["PATH_INFO"], env["QUERY_STRING"], env["HTTP_X_TEST"]]
    if scenario == "filestorage":
        source = io.BytesIO(b"payload")
        storage = FileStorage(source, filename="data.txt", content_type="text/plain")
        target = io.BytesIO()
        storage.save(target)
        return [storage.filename, storage.mimetype, target.getvalue().decode()]
    if scenario == "repr_headers":
        return repr(Headers([("X-Test", "yes")]))
    if scenario == "header_delete":
        h = Headers([("X-Test", "yes"), ("Other", "ok")])
        del h["x-test"]
        return [h.get("X-Test"), h.to_wsgi_list()]
    if scenario == "routing_missing":
        adapter = Map([Rule("/user/<int:id>", endpoint="user")]).bind("example.test")
        try:
            adapter.match("/missing")
        except Exception as exc:
            return typename(exc)
        return None
    if scenario == "bad_password":
        return check_password_hash("not-a-valid-hash", "secret")
    if scenario == "cookie_empty":
        return dump_cookie("empty")
    raise ValueError(scenario)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--scenario", required=True)
    args = parser.parse_args()
    if os.path.realpath(args.candidate_site) != "/tmp/candidate-site":
        raise ValueError("candidate site is unavailable")
    dependency_site = "/opt/candidate-dependencies/site"
    if os.path.isdir(dependency_site):
        sys.path.insert(0, dependency_site)
    sys.path.insert(0, args.candidate_site)
    try:
        print(json.dumps({"ok": True, "value": run(args.scenario)}, sort_keys=True, default=str))
    except BaseException as exc:
        print(json.dumps({"ok": False, "exception_type": typename(exc), "exception_message": str(exc)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
