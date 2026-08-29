from __future__ import annotations

import json
import importlib.machinery
import os
from array import array
from pathlib import Path
import sys

SITE = os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site")
DEPS = os.environ.get("NL2REPO_CANDIDATE_DEPENDENCIES", "/opt/candidate-dependencies/site")
sys.path[:0] = [SITE, DEPS]

import httptools


RESPONSE = (
    b"HTTP/1.1 200 OK\r\n"
    b"Date: Mon, 23 May 2005 22:38:34 GMT\r\n"
    b"Server: example\r\n"
    b"Content-Type: text/plain\r\n"
    b"Content-Length: 5\r\n"
    b"Connection: close\r\n\r\nhello"
)
UPGRADE_REQUEST = (
    b"GET /chat HTTP/1.1\r\nHost: example.test\r\n"
    b"Connection: Upgrade\r\nUpgrade: websocket\r\n\r\nraw"
)


def text(value: bytes | None) -> str | None:
    return value.decode("latin1") if value is not None else None


def jsonable(value: object) -> object:
    if isinstance(value, bytes):
        return text(value)
    if isinstance(value, tuple):
        return [jsonable(item) for item in value]
    if isinstance(value, list):
        return [jsonable(item) for item in value]
    if isinstance(value, dict):
        return {text(key) if isinstance(key, bytes) else str(key): jsonable(item) for key, item in value.items()}
    return value


class Callbacks:
    def __init__(self, failing: str | None = None) -> None:
        self.events: list[list[object]] = []
        self.failing = failing

    def _record(self, name: str, *args: object) -> None:
        if name == self.failing:
            raise RuntimeError("callback boom")
        self.events.append([name, *[jsonable(arg) for arg in args]])

    def on_message_begin(self) -> None: self._record("begin")
    def on_url(self, value: bytes) -> None: self._record("url", value)
    def on_header(self, name: bytes, value: bytes) -> None: self._record("header", name, value)
    def on_headers_complete(self) -> None: self._record("headers")
    def on_body(self, value: bytes) -> None: self._record("body", value)
    def on_message_complete(self) -> None: self._record("complete")
    def on_chunk_header(self) -> None: self._record("chunk-header")
    def on_chunk_complete(self) -> None: self._record("chunk-complete")
    def on_status(self, value: bytes) -> None: self._record("status", value)


def request_basic() -> object:
    protocol = Callbacks()
    parser = httptools.HttpRequestParser(protocol)
    parser.feed_data(b"GET /hello?x=1 HTTP/1.1\r\nHost: example.test\r\nConnection: close\r\n\r\n")
    return {"events": protocol.events, "method": text(parser.get_method()), "version": parser.get_http_version(), "keep_alive": parser.should_keep_alive(), "upgrade": parser.should_upgrade()}


def package_surface() -> object:
    modules = ["parser", "parser.protocol", "parser.errors", "parser.parser", "parser.url_parser"]
    from httptools.parser import parser as parser_module
    from httptools.parser import url_parser as url_parser_module

    native = [
        any(str(module.__file__).endswith(suffix) for suffix in importlib.machinery.EXTENSION_SUFFIXES)
        for module in (parser_module, url_parser_module)
    ]
    return {
        "version": httptools.__version__,
        "exports": sorted(httptools.__all__),
        "modules": [__import__("httptools." + name) is not None for name in modules],
        "native": native,
    }


def request_chunked() -> object:
    protocol = Callbacks()
    parser = httptools.HttpRequestParser(protocol)
    parser.feed_data(b"POST /upload HTTP/1.1\r\nTransfer-Encoding: chunked\r\n\r\n5\r\nhello\r\n6\r\n world\r\n0\r\n\r\n")
    return {"events": protocol.events, "method": text(parser.get_method())}


def request_upgrade() -> object:
    protocol = Callbacks()
    parser = httptools.HttpRequestParser(protocol)
    try:
        parser.feed_data(UPGRADE_REQUEST)
    except httptools.HttpParserUpgrade as exc:
        offset = int(exc.args[0])
    else:
        offset = -1
    return {"offset_tail": text(UPGRADE_REQUEST[offset:]) if offset >= 0 else None, "upgrade": parser.should_upgrade(), "events": protocol.events}


def request_lenient() -> object:
    protocol = Callbacks()
    parser = httptools.HttpRequestParser(protocol)
    parser.set_dangerous_leniencies(lenient_headers=True, lenient_optional_lf_after_cr=True)
    parser.feed_data(b"GET / HTTP/1.1\r\nHost: example.test\r\n\r\n")
    return {"method": text(parser.get_method()), "events": protocol.events}


def request_fragmented() -> object:
    protocol = Callbacks()
    parser = httptools.HttpRequestParser(protocol)
    message = b"PUT / HTTP/1.1\r\nHost: localhost\r\nContent-Length: 4\r\n\r\ndata"
    for byte in message:
        parser.feed_data(bytes([byte]))
    return {"events": protocol.events, "method": text(parser.get_method())}


def request_input_types() -> object:
    values: list[str] = []
    for data in (bytearray(b"GET /a HTTP/1.1\r\n\r\n"), memoryview(b"GET /b HTTP/1.1\r\n\r\n"), array("B", b"GET /c HTTP/1.1\r\n\r\n")):
        protocol = Callbacks()
        parser = httptools.HttpRequestParser(protocol)
        parser.feed_data(data)
        values.append(str(next(event[1] for event in protocol.events if event[0] == "url")))
    return values


def request_invalid() -> object:
    results: list[str] = []
    for data in (b"SPAM / HTTP/1.1", b"POST HTTP/1.1"):
        try:
            httptools.HttpRequestParser(None).feed_data(data)
        except BaseException as exc:
            results.append(type(exc).__name__)
    return results


def callback_error() -> object:
    result: dict[str, object] = {}
    for callback in ("begin", "url", "headers", "header", "body", "complete"):
        protocol = Callbacks(callback)
        parser = httptools.HttpRequestParser(protocol)
        try:
            parser.feed_data(b"POST / HTTP/1.1\r\nHost: x\r\nContent-Length: 1\r\n\r\nx")
        except BaseException as exc:
            result[callback] = [type(exc).__name__, type(exc.__context__).__name__ if exc.__context__ else None]
        else:
            result[callback] = ["none", None]
    return result


def request_keep_alive() -> object:
    protocol = Callbacks()
    parser = httptools.HttpRequestParser(protocol)
    parser.feed_data(b"GET / HTTP/1.1\r\nHost: x\r\n\r\n")
    return [parser.get_http_version(), parser.should_keep_alive(), parser.should_upgrade()]


def response_basic() -> object:
    protocol = Callbacks()
    parser = httptools.HttpResponseParser(protocol)
    parser.feed_data(RESPONSE)
    headers = [[event[1], event[2]] for event in protocol.events if event[0] == "header"]
    bodies = [event[1] for event in protocol.events if event[0] == "body"]
    return {"status": parser.get_status_code(), "version": parser.get_http_version(), "headers": headers, "bodies": bodies, "events": [event[0] for event in protocol.events]}


def response_upgrade() -> object:
    protocol = Callbacks()
    parser = httptools.HttpResponseParser(protocol)
    data = b"HTTP/1.1 101 Switching Protocols\r\nConnection: upgrade\r\nUpgrade: websocket\r\n\r\nraw"
    try:
        parser.feed_data(data)
    except httptools.HttpParserUpgrade as exc:
        tail = text(data[int(exc.args[0]):])
    else:
        tail = None
    return {"status": parser.get_status_code(), "tail": tail, "upgrade": parser.should_upgrade(), "events": [event[0] for event in protocol.events]}


def response_invalid() -> object:
    results: list[str] = []
    for data in (b"12123123", b"HTTP/1.1 1299 BAD\r\n"):
        try:
            httptools.HttpResponseParser(None).feed_data(data)
        except BaseException as exc:
            results.append(type(exc).__name__)
    return results


def response_input_types() -> object:
    values: list[int] = []
    for data in (bytearray(RESPONSE), memoryview(RESPONSE), array("B", RESPONSE)):
        parser = httptools.HttpResponseParser(None)
        parser.feed_data(data)
        values.append(parser.get_status_code())
    return values


def response_callback_error() -> object:
    protocol = Callbacks("status")
    parser = httptools.HttpResponseParser(protocol)
    try:
        parser.feed_data(RESPONSE)
    except BaseException as exc:
        return [type(exc).__name__, type(exc.__context__).__name__ if exc.__context__ else None]
    return ["none", None]


def url_components() -> object:
    value = httptools.parse_url(b"https://user:pass@example.test:8443/a/b?q=1#frag")
    return {name: text(getattr(value, name)) if name != "port" else value.port for name in ("schema", "host", "port", "path", "query", "fragment", "userinfo")}


def url_paths() -> object:
    return [jsonable(tuple(getattr(httptools.parse_url(url), name) for name in ("schema", "host", "port", "path", "query", "fragment", "userinfo"))) for url in (b"////", b"/a/b?x=1&", b"http://[1:2::3:4]:67/")]


def url_input_types() -> object:
    return [text(httptools.parse_url(data).path) for data in (bytearray(b"/"), memoryview(b"/x"), array("B", b"/y"))]


def url_invalid() -> object:
    results: list[str] = []
    for data in (b"", b" ", b":///1", b"dsf://a\x00aa", b"http://h/" + b"a" * 65535):
        try:
            httptools.parse_url(data)
        except BaseException as exc:
            results.append(type(exc).__name__)
    return results


def url_immutable() -> object:
    value = httptools.parse_url(b"/")
    try:
        value.port = 0
    except BaseException as exc:
        return [type(exc).__name__, str(exc)]
    return ["none", ""]


OPERATIONS = {name: value for name, value in globals().items() if callable(value) and name in {
    "package_surface", "request_basic", "request_chunked", "request_upgrade", "request_lenient", "request_fragmented",
    "request_input_types", "request_invalid", "callback_error", "request_keep_alive", "response_basic",
    "response_upgrade", "response_invalid", "response_input_types", "response_callback_error", "url_components", "url_paths",
    "url_input_types", "url_invalid", "url_immutable",
}}


for line in sys.stdin:
    request = json.loads(line)
    name = request.get("operation")
    try:
        result = OPERATIONS[name]()
        response = {"id": request.get("id"), "ok": True, "result": jsonable(result)}
    except BaseException as exc:
        response = {"id": request.get("id"), "ok": False, "error": {"type": type(exc).__name__, "message": str(exc)}}
    print(json.dumps(response, sort_keys=True), flush=True)
