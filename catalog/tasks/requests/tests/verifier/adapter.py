from __future__ import annotations

import base64
import io
import json
import pickle
import sys
from collections import deque
from http.cookiejar import CookieJar


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _response(requests, status=200, content=b"", headers=None, url=None):
    response = requests.Response()
    response.status_code = status
    response._content = content
    response.headers.update(headers or {})
    response.url = url or "https://example.test/"
    response.reason = requests.status_codes._codes.get(status, [""])[0].replace("_", " ").title()
    return response


def packaging(requests):
    expected = {"Session", "Request", "PreparedRequest", "Response", "get", "post", "codes"}
    return {"version": requests.__version__, "all_names": expected.issubset(set(requests.__all__))}


def case_insensitive(requests):
    d = requests.structures.CaseInsensitiveDict({"Content-Type": "text/plain", "X-ID": "1"})
    d["content-type"] = "application/json"
    return {"lookup": d["CONTENT-TYPE"], "keys": list(d), "equal": d == {"CONTENT-TYPE": "application/json", "x-id": "1"}, "lower": list(d.lower_items())}


def lookup_dict(requests):
    d = requests.structures.LookupDict("status")
    d.ok = 200
    return {"item": d["ok"], "attribute": d.ok, "missing": d["missing"], "repr": repr(d)}


def request_prepare(requests):
    req = requests.Request("get", "https://example.test/path#frag", params=[("a", "1"), ("q", "a b")], headers={"X-Test": "yes"})
    prepared = req.prepare()
    return {"method": prepared.method, "url": prepared.url, "path_url": prepared.path_url, "header": prepared.headers["x-test"], "fragment": "#frag" in prepared.url}


def json_body(requests):
    prepared = requests.Request("POST", "https://example.test/", json={"n": 2, "ok": True}).prepare()
    return {"body": prepared.body.decode("utf-8"), "content_type": prepared.headers["Content-Type"], "length": prepared.headers["Content-Length"]}


def form_body(requests):
    prepared = requests.Request("POST", "https://example.test/", data=[("a", "1"), ("a", "2"), ("q", "a b")]).prepare()
    body = prepared.body.decode("ascii") if isinstance(prepared.body, bytes) else prepared.body
    return {"body": body, "content_type": prepared.headers["Content-Type"], "length": prepared.headers["Content-Length"]}


def response_decode(requests):
    response = _response(requests, content=b'{"name":"Ada","n":2}', headers={"Content-Type": "application/json; charset=utf-8"})
    return {"content": response.content.decode("ascii"), "text": response.text, "json": response.json(), "ok": bool(response)}


def response_iter(requests):
    chunks_response = _response(requests, content=False)
    chunks_response.raw = io.BytesIO(b"aa\nbb\ncc")
    lines_response = _response(requests, content=False)
    lines_response.raw = io.BytesIO(b"aa\nbb\ncc")
    return {"chunks": [chunk.decode("ascii") for chunk in chunks_response.iter_content(2)], "lines": [line.decode("ascii") for line in lines_response.iter_lines()]}


def response_status(requests):
    response = _response(requests, 404, b"no", url="https://example.test/missing")
    try:
        response.raise_for_status()
    except requests.HTTPError as error:
        raised = {"type": type(error).__name__, "has_status": "404" in str(error), "request": error.request is response.request}
    else:
        raised = None
    return {"ok": response.ok, "redirect": response.is_redirect, "raised": raised}


def basic_auth(requests):
    prepared = requests.Request("GET", "https://example.test/").prepare()
    requests.auth.HTTPBasicAuth("Aladdin", "open sesame")(prepared)
    return {"header": prepared.headers["Authorization"], "expected": "Basic " + base64.b64encode(b"Aladdin:open sesame").decode()}


def cookies(requests):
    jar = requests.cookies.cookiejar_from_dict({"sid": "abc", "theme": "dark"})
    jar.set("scoped", "yes", domain="example.test", path="/")
    prepared = requests.Request("GET", "https://example.test/items").prepare()
    prepared.prepare_cookies(jar)
    return {"dict": requests.utils.dict_from_cookiejar(jar), "header": prepared.headers["Cookie"], "domain": jar.get_dict(domain="example.test")}


def session_prepare(requests):
    session = requests.Session()
    session.headers.update({"X-Session": "yes"})
    session.cookies.set("sid", "abc", domain="example.test", path="/")
    prepared = session.prepare_request(requests.Request("GET", "https://example.test/items", headers={"X-Request": "one"}))
    return {"session_header": prepared.headers["x-session"], "request_header": prepared.headers["x-request"], "cookie": prepared.headers["Cookie"], "url": prepared.url}


def adapter_session(requests):
    class LocalAdapter(requests.adapters.BaseAdapter):
        def __init__(self):
            self.seen = []
            self.closed = False

        def send(self, request, **kwargs):
            self.seen.append({"method": request.method, "url": request.url, "body": request.body})
            result = _response(requests, content=b"adapter", url=request.url)
            result.request = request
            result.connection = self
            return result

        def close(self):
            self.closed = True

    adapter = LocalAdapter()
    session = requests.Session()
    session.mount("https://", adapter)
    result = session.post("https://example.test/submit", data={"x": "1"}, headers={"X-Local": "ok"})
    return {"status": result.status_code, "body": result.content.decode("ascii"), "request_method": result.request.method, "seen": [{"method": item["method"], "url": item["url"], "body": item["body"] if isinstance(item["body"], str) else (item["body"].decode("ascii") if item["body"] is not None else None)} for item in adapter.seen], "closed_before": adapter.closed}


def hooks(requests):
    events = []

    class LocalAdapter(requests.adapters.BaseAdapter):
        def send(self, request, **kwargs):
            result = _response(requests, content=b"hook", url=request.url)
            result.request = request
            return result

        def close(self):
            pass

    def hook(response, **kwargs):
        events.append((response.status_code, kwargs.get("stream")))
        response.headers["X-Hooked"] = "yes"
        return response

    session = requests.Session()
    session.mount("https://", LocalAdapter())
    result = session.get("https://example.test/", hooks={"response": hook}, stream=True)
    return {"events": events, "header": result.headers["X-Hooked"], "content": result.content.decode("ascii")}


def redirects(requests):
    class RedirectAdapter(requests.adapters.BaseAdapter):
        def __init__(self, statuses):
            self.statuses = deque(statuses)
            self.seen = []

        def send(self, request, **kwargs):
            self.seen.append({"method": request.method, "url": request.url, "body": request.body})
            status, headers, body = self.statuses.popleft()
            result = _response(requests, status, body, headers, request.url)
            result.request = request
            result.connection = self
            return result

        def close(self):
            pass

    adapter = RedirectAdapter([(302, {"Location": "/next"}, b""), (200, {}, b"ok")])
    session = requests.Session()
    session.mount("https://", adapter)
    result = session.get("https://example.test/start#fragment")
    return {"status": result.status_code, "history": [item.status_code for item in result.history], "final": result.url, "seen": adapter.seen}


def redirect_methods(requests):
    class RedirectAdapter(requests.adapters.BaseAdapter):
        def __init__(self, status):
            self.status = status
            self.seen = []
            self.count = 0

        def send(self, request, **kwargs):
            self.seen.append((request.method, request.body, request.headers.get("Content-Length")))
            self.count += 1
            if self.count == 1:
                result = _response(requests, self.status, {"Location": "/next"}, url=request.url)
                result.headers["Location"] = "/next"
            else:
                result = _response(requests, 200, b"ok", url=request.url)
            result.request = request
            result.connection = self
            return result

        def close(self):
            pass

    def trace(status):
        adapter = RedirectAdapter(status)
        session = requests.Session()
        session.mount("https://", adapter)
        result = session.post("https://example.test/start", data="body")
        return {"status": result.status_code, "seen": adapter.seen}

    return {"post302": trace(302), "post307": trace(307)}


def utilities(requests):
    return {
        "dict_header": requests.utils.parse_dict_header('a=1, b="two"'),
        "list_header": requests.utils.parse_list_header('one, "two words", three'),
        "links": requests.utils.parse_header_links('<https://example.test/2>; rel="next"'),
        "slices": list(requests.utils.iter_slices("abcdef", 2)),
        "auth": requests.utils.get_auth_from_url("https://u:p@example.test/path"),
        "requote": requests.utils.requote_uri("https://example.test/a b"),
        "defrag": requests.utils.urldefragauth("https://u:p@example.test/path#frag"),
    }


def status_codes(requests):
    return {"ok": requests.codes.ok, "found": requests.codes.found, "missing": requests.codes.not_found, "too_many": requests.codes.too_many_requests}


def prepared_copy(requests):
    original = requests.Request("PUT", "https://example.test/", data="x", headers={"X": "1"}).prepare()
    copied = original.copy()
    copied.headers["X"] = "2"
    return {"same_url": copied.url == original.url, "same_body": copied.body == original.body, "independent_headers": original.headers["X"] == "1", "repr": "PreparedRequest" in repr(copied)}


def response_links(requests):
    response = _response(requests, content=b"", headers={"Link": '<https://example.test/2>; rel="next", <https://example.test/0>; rel="prev"'})
    return response.links


def session_close(requests):
    class LocalAdapter(requests.adapters.BaseAdapter):
        def __init__(self):
            self.closed = False
        def send(self, request, **kwargs):
            result = _response(requests, url=request.url)
            result.request = request
            return result
        def close(self):
            self.closed = True
    adapter = LocalAdapter()
    session = requests.Session()
    session.mount("https://", adapter)
    session.close()
    return {"closed": adapter.closed, "adapters": len(session.adapters)}


OPERATIONS = {name: globals()[name] for name in (
    "packaging", "case_insensitive", "lookup_dict", "request_prepare", "json_body", "form_body",
    "response_decode", "response_iter", "response_status", "basic_auth", "cookies", "session_prepare",
    "adapter_session", "hooks", "redirects", "redirect_methods", "utilities", "status_codes",
    "prepared_copy", "response_links", "session_close",
)}


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--dependency-site", required=False)
    parser.add_argument("--request", required=True)
    args = parser.parse_args()
    sys.path.insert(0, args.candidate_site)
    if args.dependency_site:
        sys.path.insert(1, args.dependency_site)
    import requests
    request = json.loads(args.request)
    operation = request["operation"]
    try:
        value = OPERATIONS[operation](requests)
        print(_json({"ok": True, "value": value}))
    except Exception as error:
        print(_json({"ok": False, "exception_type": type(error).__name__, "exception_message": str(error)}))


if __name__ == "__main__":
    main()
